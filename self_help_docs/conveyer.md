# 🧭 Linear Execution Plan — 13-Day Assault Plan

> Goal: Ship a coherent, intelligent Assistant Coach that demonstrably links micro mistakes to macro outcomes, within 13 calendar days.
>
> Rule: Never start the next chunk until the current chunk produces a concrete artifact committed to the repo.

---

## 🟦 CHUNK 0 — Dataset Acquisition (Day 1)

### 🎯 Objective

Obtain a usable historical match dataset (real or synthetic) suitable for analytics and demo.

### 🛠️ Actions

* Identify public esports dataset OR
* Programmatically generate synthetic match data
* Ensure schema stability

### 📥 Inputs

None

### 📤 Outputs

* `data/matches.csv`
* Dataset schema documented

### ✅ Completion Criteria

* File loads into pandas
* ≥100k rows
* Stable columns

### ⏱️ Time Budget

6–8 hours

---

## 🟦 CHUNK 1 — Data Loader & Cleaning (Day 2)

### 🎯 Objective

Create a robust ingestion pipeline.

### 🛠️ Actions

* Pandas loader
* Schema validation
* Type normalization
* Missing value handling
* Basic stats logging

### 📥 Inputs

* `matches.csv`

### 📤 Outputs

* `df_clean`
* Data validation report

### ✅ Completion Criteria

* No NaNs in critical fields
* Consistent dtypes
* Load time <2s

### ⏱️ Time Budget

5–6 hours

---

## 🟦 CHUNK 2 — Feature Engineering (Days 3–4)

### 🎯 Objective

Derive analytics-ready features.

### 🛠️ Actions

Compute:

* Time to engagement
* Average distance to teammates
* Exposure duration
* Damage before trade
* Economy efficiency
* Movement entropy

### 📥 Inputs

* `df_clean`

### 📤 Outputs

* `df_features`

### ✅ Completion Criteria

* All feature columns exist
* Reasonable distributions
* No exploding values

### ⏱️ Time Budget

10–12 hours

---

## 🟦 CHUNK 3 — Micro Mistake Detectors (Days 5–6)

### 🎯 Objective

Detect recurring player mistakes.

### 🛠️ Actions

Implement rule-based detectors:

* Over-peeking
* Late trading
* Poor spacing
* Ability waste
* Economy misplay

Each outputs boolean + severity.

### 📥 Inputs

* `df_features`

### 📤 Outputs

* `mistake_events.csv`

### ✅ Completion Criteria

* Mistake counts realistic
* Severity normalized

### ⏱️ Time Budget

10–12 hours

---

## 🟦 CHUNK 4 — Macro KPI Computation (Day 7)

### 🎯 Objective

Compute team-level outcomes.

### 🛠️ Actions

Compute:

* Round win rate
* Entry success
* Trade conversion
* Economy stability
* Objective success

### 📥 Inputs

* Raw match data

### 📤 Outputs

* `kpi_table.csv`

### ✅ Completion Criteria

* Aggregates verified

### ⏱️ Time Budget

6–8 hours

---

## 🟦 CHUNK 5 — Micro → Macro Attribution (Days 8–9)

### 🎯 Objective

Estimate causal impact.

### 🛠️ Actions

* Stratified comparison
* KPI delta computation
* Stability estimation

### 📥 Inputs

* `mistake_events`
* `kpi_table`

### 📤 Outputs

* `impact_table.csv`

### ✅ Completion Criteria

* Each mistake has impact score
* Stable ranking

### ⏱️ Time Budget

12–14 hours

---

## 🟦 CHUNK 6 — Ranking Engine (Day 10)

### 🎯 Objective

Identify top loss drivers.

### 🛠️ Actions

* Scoring formula
* Normalization
* Sorting

### 📥 Inputs

* `impact_table`

### 📤 Outputs

* `ranked_causes.csv`

### ✅ Completion Criteria

* Ranking stable across runs

### ⏱️ Time Budget

4–6 hours

---

## 🟦 CHUNK 7 — Counterfactual Simulator (Day 11)

### 🎯 Objective

Simulate improvements.

### 🛠️ Actions

* Slider controls
* KPI recomputation
* Delta visualization

### 📥 Inputs

* `ranked_causes`

### 📤 Outputs

* Simulation module

### ✅ Completion Criteria

* Real-time updates

### ⏱️ Time Budget

4–6 hours

---

## 🟦 CHUNK 8 — UI Integration (Day 12)

### 🎯 Objective

Deliver interactive dashboard.

### 🛠️ Actions

* Streamlit layout
* Charts
* Filters

### 📥 Inputs

* All prior outputs

### 📤 Outputs

* Running app

### ✅ Completion Criteria

* Smooth demo flow

### ⏱️ Time Budget

6–8 hours

---

## 🟦 CHUNK 9 — Demo & Polish (Day 13)

### 🎯 Objective

Finalize presentation.

### 🛠️ Actions

* Script demo
* Record backup video
* Clean README

### 📥 Inputs

* Working app

### 📤 Outputs

* Demo assets

### ✅ Completion Criteria

* Confident demo under 4 min

### ⏱️ Time Budget

4–6 hours

---

## 🛑 Discipline Rules

* No scope expansion
* No redesign loops
* Commit daily
* Demo must always run
* Finish beats perfect

---
