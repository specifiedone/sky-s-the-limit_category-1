#!/usr/bin/env python3
"""
VLR Dev API data collector for esports match data.

Uses the vlrdevapi Python library to fetch official Valorant match data,
normalize into analytics schema, and export for analysis.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

try:
    import vlrdevapi
except ImportError:
    print("Error: vlrdevapi not installed. Install with: pip install vlrdevapi")
    exit(1)


# =====================
# Configuration
# =====================

@dataclass
class CollectorConfig:
    output_path: str
    output_format: str  # csv | parquet
    max_matches: int
    logging_level: str
    team_filter: Optional[str] = None  # optional: filter by team


# =====================
# Schema Models
# =====================

@dataclass
class Team:
    team_id: str
    name: Optional[str] = None
    region: Optional[str] = None


@dataclass
class Match:
    match_id: str
    source: str
    start_time: Optional[datetime]
    patch: Optional[str]
    tournament: Optional[str]
    teams: List[str]
    status: Optional[str] = None


@dataclass
class Map:
    map_id: str
    match_id: str
    name: Optional[str]
    winner_team_id: Optional[str]


@dataclass
class Player:
    player_id: str
    handle: Optional[str] = None
    team_id: Optional[str] = None


# =====================
# VLR Data Collector
# =====================

class VLRDataCollector:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.client = vlrdevapi.VLR()
        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self.config.logging_level.upper(), logging.INFO),
            format="%(asctime)s %(levelname)s %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def fetch_matches(self) -> List[Dict[str, Any]]:
        """Fetch recent matches from VLR API."""
        try:
            self.logger.info("Fetching matches from VLR API...")
            matches = self.client.get_matches()
            
            if not matches:
                self.logger.warning("No matches returned from API")
                return []
            
            # Limit to max_matches
            limited_matches = matches[: self.config.max_matches]
            self.logger.info(f"Fetched {len(limited_matches)} matches")
            return limited_matches
            
        except Exception as e:
            self.logger.error(f"Error fetching matches: {e}")
            return []

    def normalize_match(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a raw VLR match into canonical schema."""
        try:
            match_id = raw.get("id") or raw.get("match_id")
            if not match_id:
                self.logger.warning("Match missing ID")
                return None

            teams = raw.get("teams", [])
            team_ids = []
            team_objects = []

            for team in teams:
                team_id = team.get("id") or team.get("name", "unknown")
                team_ids.append(team_id)
                team_objects.append({
                    "team_id": team_id,
                    "name": team.get("name"),
                    "region": team.get("region"),
                })

            # Parse timestamp
            start_time = None
            if raw.get("date"):
                try:
                    start_time = datetime.fromisoformat(
                        raw["date"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            match_data = {
                "match_id": str(match_id),
                "source": "vlr",
                "start_time": start_time,
                "patch": raw.get("patch"),
                "tournament": raw.get("event") or raw.get("tournament"),
                "teams": team_ids,
                "status": raw.get("status"),
            }

            return {
                "match": match_data,
                "teams": team_objects,
            }

        except Exception as e:
            self.logger.error(f"Error normalizing match {raw.get('id')}: {e}")
            return None

    def collect(self) -> None:
        """Main collection pipeline."""
        raw_matches = self.fetch_matches()
        
        if not raw_matches:
            self.logger.warning("No data to process")
            return

        matches = []
        teams = []
        seen_teams = set()

        for raw_match in raw_matches:
            normalized = self.normalize_match(raw_match)
            if not normalized:
                continue

            matches.append(normalized["match"])
            
            # Collect unique teams
            for team in normalized["teams"]:
                team_id = team["team_id"]
                if team_id not in seen_teams:
                    teams.append(team)
                    seen_teams.add(team_id)

        # Create DataFrames
        df_matches = pd.DataFrame(matches)
        df_teams = pd.DataFrame(teams)

        # Create output directory
        out_path = Path(self.config.output_path)
        out_path.mkdir(parents=True, exist_ok=True)

        # Export data
        ext = "parquet" if self.config.output_format == "parquet" else "csv"
        
        if self.config.output_format == "parquet":
            df_matches.to_parquet(out_path / f"matches.parquet", index=False)
            df_teams.to_parquet(out_path / f"teams.parquet", index=False)
        else:
            df_matches.to_csv(out_path / f"matches.csv", index=False)
            df_teams.to_csv(out_path / f"teams.csv", index=False)

        self.logger.info(f"✓ Export complete")
        self.logger.info(f"  matches: {len(df_matches)} rows → {out_path}/matches.{ext}")
        self.logger.info(f"  teams: {len(df_teams)} rows → {out_path}/teams.{ext}")


# =====================
# CLI
# =====================

def load_config(path: str) -> CollectorConfig:
    """Load configuration from YAML file."""
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    
    # Extract collector-specific config
    collector_config = {
        "output_path": raw.get("output_path", "./data/output"),
        "output_format": raw.get("output_format", "csv"),
        "max_matches": raw.get("max_matches_to_fetch", 10),
        "logging_level": raw.get("logging_level", "INFO"),
        "team_filter": raw.get("team_filter"),
    }
    return CollectorConfig(**collector_config)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect Valorant esports data from VLR API"
    )
    parser.add_argument(
        "--config",
        default="./data/config.yaml",
        help="Path to config YAML (default: ./data/config.yaml)",
    )
    args = parser.parse_args()
    
    config = load_config(args.config)
    collector = VLRDataCollector(config)
    collector.collect()


if __name__ == "__main__":
    main()
