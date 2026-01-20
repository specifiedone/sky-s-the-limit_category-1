# 🏆 What To Build — Assistant Coach (Winning Spec)

> Purpose: A narrow, execution-focused product spec that documents exactly what is being built, why it exists, and how each capability compounds toward winning the hackathon.
>
> This file doubles as:
>
> * Internal execution contract
> * Public build log narrative
> * Scope guardrail

---

## 🎯 Product Goal

Build a **near‑real‑time Assistant Coach** that:

1. Detects **recurring micro‑level player mistakes**
2. Quantifies how those mistakes impact **macro‑level team outcomes**
3. Ranks **true loss drivers (causal impact, not correlation)**
4. Generates **actionable coaching recommendations**
5. Supports **interactive exploration + demo clarity**

The system must feel intelligent, grounded, and deterministic — not a chatbot, not a dashboard toy.

---

## 🧱 Core Design Principles

* **Causality over Correlation**
* **Explainability over Black Box ML**
* **Deterministic Outputs (same input → same result)**
* **Fast iteration over perfection**
* **Demo-first engineering**
* **Minimal scope, maximum signal density**

---

## 📦 Data Scope (Phase 1)

### Input Data

Historical match dataset (CSV / Parquet):

Per round / tick features:

* Match ID
* Round number
* Player ID
* Agent / role
* Position (x,y or zone)
* Health
* Economy
* Weapon
* Kill / death / damage events
* Ability usage
* Objective events (plant / defuse / spike control)
* Timestamp

Derived features (computed):

* Time to first contact
* Exposure time
* Trade delay
* Distance to nearest teammate
* Crosshair alignment proxy
* Ability timing deviation
* Economy efficiency
* Positional entropy

---

## 🧠 Analytics Pipeline

### 1️⃣ Micro Mistake Detection Engine

Detects repeatable player‑level mistakes:

Examples:

* Over‑peeking frequency
* Late trade support
* Poor spacing
* Ability waste
* Unsafe reload timing
* Economic mismanagement
* Position overexposure

Each mistake outputs:

* Frequency
* Severity score
* Consistency score
* Affected rounds

---

### 2️⃣ Macro Outcome Modeling

Team-level outcomes:

* Round win probability
* Entry success rate
* Trade conversion
* Site control time
* Economy stability
* Post‑plant success

Computed per match + per segment.

---

### 3️⃣ Micro → Macro Impact Attribution

Core differentiator.

For each micro mistake type:

* Measure delta impact on macro KPIs
* Control for confounders using stratification
* Estimate marginal contribution
* Stability across samples

Outputs:

```
Mistake → KPI Impact → Confidence → Rank
```

---

### 4️⃣ Causal Ranking Engine

Ranks mistakes by:

Score = Impact × Frequency × Stability × Strategic Weight

Produces:

* Top 5 loss drivers
* Supporting evidence
* Affected players
* Expected improvement if corrected

---

### 5️⃣ Counterfactual Simulator (Lightweight)

Simulates partial correction scenarios:

* Reduce mistake frequency by X%
* Estimate KPI lift
* Show projected win impact

Pure statistical simulation (not ML heavy).

---

## 🎛️ Product Interface

### Main Dashboard

Panels:

1. Team Health Summary
2. Top Loss Drivers
3. Micro → Macro Impact Graph
4. Player Mistake Breakdown
5. Counterfactual Simulator

All panels must cross‑filter.

---

### Drilldown Views

* Player profile
* Mistake timeline
* Impact evidence table

---

## 🎬 Demo Narrative Flow

1. Load match dataset
2. Show team baseline metrics
3. Reveal top loss drivers
4. Drill into one mistake
5. Show causal evidence
6. Simulate improvement
7. Show projected impact

Target demo length: 3–4 minutes.

---

## 🧪 Validation Metrics

System quality indicators:

* Stability across reruns
* Signal sparsity (few high‑value insights)
* Interpretability
* Demo reliability
* Runtime under 5s per dataset

---

## 🛑 Explicit Non‑Goals

Do NOT build:

* Live game integration
* Real-time streaming ingestion
* Deep neural models
* Chatbot interfaces
* Fancy UI animations
* Multi-game support
* Account systems
* Cloud deployment
* Mobile optimization

---

## 🗺️ Execution Phases

Phase 1 — Data ingestion + feature extraction
Phase 2 — Micro mistake detectors
Phase 3 — Macro KPI computation
Phase 4 — Attribution engine
Phase 5 — Ranking logic
Phase 6 — Simulator
Phase 7 — UI + demo polish

---

## 📈 Stretch Upgrades (Only If Ahead of Schedule)

* Temporal causality graph
* Automated insight text generator
* Session comparison mode
* Coach recommendation templates
* Confidence bands

Only build after core stability.

---

## 🧨 Personal Discipline Contract

* No scope expansion without justification
* No redesign unless blocked
* Ship something usable every day
* Demo always runs
* Evidence beats elegance
* Finish > perfect

---

## 🏁 Definition of Done

* Dataset loads successfully
* Top loss drivers computed
* Causal impact visible
* Simulator works
* UI stable
* Demo story coherent
* Repo reflects progressive commits

---
