#!/usr/bin/env python3
"""
Production-grade esports data ingestion pipeline.

Ingests REAL match data from public esports APIs (vlrdevapi and GRID),
normalizes into a canonical analytics schema, enriches with derived features,
validates, caches, and exports datasets for ML and analytics.

Python 3.10+
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
import yaml


# =====================
# Configuration
# =====================

@dataclass
class PipelineConfig:
    enabled_sources: List[str]
    api_keys: Dict[str, Optional[str]]
    request_limits: Dict[str, int]
    output_path: str
    output_format: str  # csv | parquet
    max_matches_to_fetch: int
    min_match_date: Optional[str]
    schema_version: str
    feature_flags: Dict[str, bool]
    caching_enabled: bool
    cache_path: str
    refresh_policy: str  # full | incremental
    logging_level: str
    timeout_seconds: int = 15
    retry_attempts: int = 3
    retry_backoff_seconds: float = 1.5


# =====================
# Schema Models
# =====================

@dataclass
class Team:
    team_id: str
    name: Optional[str] = None
    region: Optional[str] = None


@dataclass
class Player:
    player_id: str
    handle: Optional[str] = None
    team_id: Optional[str] = None


@dataclass
class Match:
    match_id: str
    source: str
    start_time: Optional[datetime]
    patch: Optional[str]
    tournament: Optional[str]
    teams: List[str] = field(default_factory=list)


@dataclass
class Map:
    map_id: str
    match_id: str
    name: Optional[str]
    winner_team_id: Optional[str]


@dataclass
class Round:
    round_id: str
    map_id: str
    round_number: int
    attacking_team_id: Optional[str]
    defending_team_id: Optional[str]
    winner_team_id: Optional[str]
    spike_planted: Optional[bool]
    spike_defused: Optional[bool]
    end_time: Optional[float]


@dataclass
class PlayerRoundStats:
    round_id: str
    player_id: str
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    first_kill: bool = False
    first_death: bool = False
    clutch_attempt: bool = False
    survived: bool = False


# =====================
# API Layer
# =====================

class ApiClient(ABC):
    def __init__(self, base_url: str, api_key: Optional[str], config: PipelineConfig):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.config = config
        self.session = requests.Session()
        self._last_request_ts = 0.0

    def _rate_limit(self) -> None:
        limit = self.config.request_limits.get(self.__class__.__name__, 1)
        elapsed = time.time() - self._last_request_ts
        if elapsed < 1.0 / max(limit, 1):
            time.sleep((1.0 / limit) - elapsed)
        self._last_request_ts = time.time()

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for attempt in range(self.config.retry_attempts):
            try:
                self._rate_limit()
                resp = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout_seconds,
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt >= self.config.retry_attempts - 1:
                    logging.error("API request failed: %s %s", url, e)
                    return None
                time.sleep(self.config.retry_backoff_seconds * (attempt + 1))
        return None

    @abstractmethod
    def fetch_matches(self) -> Iterable[Dict[str, Any]]:
        pass

    @abstractmethod
    def normalize(self, raw: Dict[str, Any]) -> Tuple[
        List[Match],
        List[Map],
        List[Round],
        List[Team],
        List[Player],
        List[PlayerRoundStats],
    ]:
        pass


class VLRClient(ApiClient):
    def __init__(self, config: PipelineConfig):
        super().__init__("https://vlrggapi.vercel.app", None, config)

    def fetch_matches(self) -> Iterable[Dict[str, Any]]:
        data = self._request("/match")
        if not data or "data" not in data:
            return []
        return data["data"][: self.config.max_matches_to_fetch]

    def normalize(self, raw: Dict[str, Any]):
        matches, maps, rounds, teams, players, prs = [], [], [], [], [], []

        match_id = str(raw.get("match_id"))
        start_time = None
        if raw.get("time"):
            start_time = datetime.fromtimestamp(int(raw["time"]), tz=timezone.utc)

        team_ids = []
        for t in raw.get("teams", []):
            tid = str(t.get("id"))
            team_ids.append(tid)
            teams.append(Team(team_id=tid, name=t.get("name")))

        matches.append(
            Match(
                match_id=match_id,
                source="vlr",
                start_time=start_time,
                patch=None,
                tournament=raw.get("event"),
                teams=team_ids,
            )
        )

        return matches, maps, rounds, teams, players, prs


class GridClient(ApiClient):
    def __init__(self, config: PipelineConfig):
        super().__init__("https://api.grid.gg/v2", config.api_keys.get("grid"), config)

    def fetch_matches(self) -> Iterable[Dict[str, Any]]:
        params = {"page[size]": self.config.max_matches_to_fetch}
        data = self._request("/matches", params=params)
        if not data or "data" not in data:
            return []
        return data["data"]

    def normalize(self, raw: Dict[str, Any]):
        matches, maps, rounds, teams, players, prs = [], [], [], [], [], []

        match_id = raw.get("id")
        start_time = None
        if raw.get("attributes", {}).get("start_time"):
            start_time = datetime.fromisoformat(
                raw["attributes"]["start_time"].replace("Z", "+00:00")
            )

        team_ids = []
        for rel in raw.get("relationships", {}).get("teams", {}).get("data", []):
            team_ids.append(rel["id"])
            teams.append(Team(team_id=rel["id"]))

        matches.append(
            Match(
                match_id=match_id,
                source="grid",
                start_time=start_time,
                patch=None,
                tournament=None,
                teams=team_ids,
            )
        )

        return matches, maps, rounds, teams, players, prs


# =====================
# Feature Engineering
# =====================

class FeatureEngineer:
    def __init__(self, flags: Dict[str, bool]):
        self.flags = flags

    def enrich_player_round_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.flags.get("survival_rate"):
            df["survived"] = df["deaths"] == 0
        if self.flags.get("aggression_index"):
            df["aggression_index"] = df["kills"] / (df["deaths"] + 1)
        if self.flags.get("consistency_index"):
            df["consistency_index"] = (
                df.groupby("player_id")["kills"].transform("mean")
            )
        return df


# =====================
# Validation
# =====================

class Validator:
    def validate_dataframe(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        if df.empty:
            return df
        null_ratio = df.isnull().mean()
        bad_cols = null_ratio[null_ratio > 0.9]
        if not bad_cols.empty:
            logging.warning("High null ratio in %s: %s", name, bad_cols.to_dict())
        return df.drop_duplicates()


# =====================
# Cache
# =====================

class CacheManager:
    def __init__(self, path: str):
        self.base = Path(path)
        self.base.mkdir(parents=True, exist_ok=True)

    def _hash(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    def load(self, key: str) -> Optional[Any]:
        fp = self.base / f"{self._hash(key)}.json"
        if fp.exists():
            with open(fp, "r") as f:
                return json.load(f)
        return None

    def save(self, key: str, data: Any) -> None:
        fp = self.base / f"{self._hash(key)}.json"
        with open(fp, "w") as f:
            json.dump(data, f)


# =====================
# Pipeline
# =====================

def run_pipeline(config: PipelineConfig) -> None:
    logging.basicConfig(
        level=getattr(logging, config.logging_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    cache = CacheManager(config.cache_path)
    validator = Validator()
    feature_engineer = FeatureEngineer(config.feature_flags)

    clients: List[ApiClient] = []
    if "vlr" in config.enabled_sources:
        clients.append(VLRClient(config))
    if "grid" in config.enabled_sources:
        clients.append(GridClient(config))

    all_matches, all_maps, all_rounds, all_teams, all_players, all_prs = (
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for client in clients:
        raw_matches = client.fetch_matches()
        for raw in raw_matches:
            key = f"{client.__class__.__name__}:{raw.get('id') or raw.get('match_id')}"
            if config.caching_enabled:
                cached = cache.load(key)
                if cached:
                    raw = cached
                else:
                    cache.save(key, raw)

            m, mp, r, t, p, prs = client.normalize(raw)
            all_matches.extend(m)
            all_maps.extend(mp)
            all_rounds.extend(r)
            all_teams.extend(t)
            all_players.extend(p)
            all_prs.extend(prs)

    df_matches = pd.DataFrame([asdict(x) for x in all_matches])
    df_maps = pd.DataFrame([asdict(x) for x in all_maps])
    df_rounds = pd.DataFrame([asdict(x) for x in all_rounds])
    df_teams = pd.DataFrame([asdict(x) for x in all_teams])
    df_players = pd.DataFrame([asdict(x) for x in all_players])
    df_prs = pd.DataFrame([asdict(x) for x in all_prs])

    df_prs = feature_engineer.enrich_player_round_stats(df_prs)

    dfs = {
        "matches": validator.validate_dataframe(df_matches, "matches"),
        "maps": validator.validate_dataframe(df_maps, "maps"),
        "rounds": validator.validate_dataframe(df_rounds, "rounds"),
        "teams": validator.validate_dataframe(df_teams, "teams"),
        "players": validator.validate_dataframe(df_players, "players"),
        "player_round_stats": validator.validate_dataframe(df_prs, "player_round_stats"),
    }

    out = Path(config.output_path)
    out.mkdir(parents=True, exist_ok=True)

    for name, df in dfs.items():
        if config.output_format == "parquet":
            df.to_parquet(out / f"{name}.parquet", index=False)
        else:
            df.to_csv(out / f"{name}.csv", index=False)

    logging.info("Ingestion complete")
    for name, df in dfs.items():
        logging.info("%s: %d rows", name, len(df))


# =====================
# CLI
# =====================

def load_config(path: str) -> PipelineConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return PipelineConfig(**raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Esports data ingestion pipeline")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    args = parser.parse_args()
    config = load_config(args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()
