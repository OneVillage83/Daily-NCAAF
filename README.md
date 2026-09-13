# Daily NCAAF

**The Daily Line — College Football Intelligence Engine**

Daily NCAAF is the college-football-specific prediction, simulation, market-evaluation, and continuous-learning system for The Daily Line.

The project is being designed as a full production architecture from the beginning rather than as a disposable MVP. The governing architecture is documented before implementation so code cannot silently redefine scientific, data, identity, point-in-time, or evaluation assumptions later.

## Core operating rules

- Predict every eligible supported game and market.
- Apply BET / LEAN / PASS / AVOID only after prediction, fair-price, edge, uncertainty, and risk evaluation.
- Store, settle, and evaluate PASS and AVOID predictions alongside BET and LEAN.
- Enforce historical point-in-time eligibility: information must be defensibly available at or before the prediction snapshot and before kickoff.
- Continue monitoring meaningful pregame information through kickoff; there is no blanket prohibition on same-day data.
- Preserve immutable raw evidence before normalization and feature engineering.
- Use canonical internal identities; provider IDs remain crosswalks.
- Preserve a broad Model Zoo rather than prematurely selecting one universal algorithm.
- Combine validated independent signal through a dynamic learned mixture-of-experts with target-, context-, uncertainty-, and data-quality-dependent weights.
- Treat validated specialists as first-class contributors even when their aggregate ranking is mediocre.
- Keep the calibrated **TDL Unified Line** independent of sportsbook, exchange, prediction-market, line-movement, and closing-price inputs.
- Keep football-only, market-only, market-aware, and ensemble forecasts explicitly distinguishable.
- Use chronological / walk-forward evaluation as the primary validation framework.
- Train stackers only from frozen forward/out-of-fold base predictions and isolate calibration from final-test evidence.
- Treat uncertainty and model disagreement as first-class model outputs.
- Preserve reproducibility and lineage for every prediction snapshot rather than overwriting reruns.
- Use a sport-specific NCAAF Line Timing Model after the independent TDL line exists to evaluate open/current/consensus/expected-close behavior and BET_NOW/WAIT timing.
- Keep closing lines evaluation-only for earlier prediction snapshots.
- Keep cross-sport infrastructure in `Daily-Data-Core` and college-football-native intelligence in `Daily-NCAAF`.
- Do not prematurely extract shared NFL/NCAAF code. Build both implementations first, then extract abstractions only where semantics are demonstrably shared.

## Architecture

The governing architecture is organized as F-0 through F-24 across six layers, supplemented by a cross-sport Unified Ensemble overlay at [`docs/architecture/TDL_UNIFIED_ENSEMBLE_OVERLAY_V1.md`](./docs/architecture/TDL_UNIFIED_ENSEMBLE_OVERLAY_V1.md):

```text
LAYER 1 — TRUTH & EVIDENCE
F-0 → F-5

LAYER 2 — FOOTBALL STATE
F-6 → F-12

LAYER 3 — FEATURES & TARGETS
F-13 → F-14

LAYER 4 — MODELING & SIMULATION
F-15 → F-17

LAYER 5 — MARKET / RECOMMENDATION / LEARNING
F-18 → F-21

LAYER 6 — NCAAF EXTENSIONS & FUTURE RESEARCH
F-22 → F-24

CROSS-SPORT GOVERNANCE OVERLAY
TDL Unified Line / Model Zoo / dynamic learned ensemble / specialist discovery /
market firewall / NCAAF Line Timing Model / immutable prediction ledger
```

The overlay standardizes the new The Daily Line-wide modeling decisions without silently changing the meaning of already locked F-layer architecture.

Architecture changes must be versioned rather than silently rewriting the meaning of an already-locked version.
