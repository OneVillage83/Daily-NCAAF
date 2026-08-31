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
- Keep football-only, market-only, market-aware, and ensemble forecasts explicitly distinguishable.
- Use chronological / walk-forward evaluation as the primary validation framework.
- Treat uncertainty as a first-class model output.
- Preserve reproducibility and lineage for published predictions.
- Keep cross-sport infrastructure in `Daily-Data-Core` and college-football-native intelligence in `Daily-NCAAF`.
- Do not prematurely extract shared NFL/NCAAF code. Build both implementations first, then extract abstractions only where semantics are demonstrably shared.

## Current phase

**Phase B — Source & Coverage Audit** is active.

- **B.1 — Public Source & Contract Audit:** complete.
- **B.2-A — CFBD games/PBP representative audit:** core complete.
- Public SportsDataverse/cfbfastR measurement is complete for the current audit pass.
- The authenticated CFBD event audit located the sampled `wallclock` coverage break between 2017 and 2018, proved that `classification=fbs` includes FBS-vs-FCS games, resolved the 2024 Liberty–App State incomplete row as a real cancellation, and showed that PPA nullness is play-family dependent.
- **B.2-B — CFBD college-native family expansion:** initial broad pass complete; focused era/scope follow-up active.
- The first B.2-B run measured teams/conference affiliations, rosters, recruiting, transfer portal, returning production, coaches, talent, rankings, ratings and historical lines across 2014/2018/2024/2026.
- Direct recruiting↔college-player linkage is useful but incomplete; provider IDs remain evidence/crosswalks rather than canonical identity.
- Transfer-portal and talent families have explicit unresolved historical floors/scope changes.
- Rating families have distinct entity-universe and temporal semantics; CORE is retrospective, and current-season readiness differs materially by model.
- Historical CFBD lines are useful market evidence but are **not** timestamped sportsbook quote tape. Daily-Data-Core remains authoritative for sportsbook identity, aliases, quote chronology and no-vig.
- B.2-C cross-provider reconciliation, B.2-D prospective live revision measurement and B.2-E availability-source trials remain before Phase C.

Current references:

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V5.md`](./docs/data/PROVIDER_PROBE_RESULTS_V5.md)
- [`docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md`](./docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md)
- [`docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md`](./docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md)

Research-only probe tooling:

- [`scripts/probes/provider_coverage_probe.py`](./scripts/probes/provider_coverage_probe.py)
- [`scripts/probes/cfbd_native_family_probe.py`](./scripts/probes/cfbd_native_family_probe.py)

Phase C canonical-schema implementation remains intentionally blocked until B.2 has enough empirical evidence to design provider-independent contracts.

## Architecture

The governing architecture lives in [`docs/architecture`](./docs/architecture) and is organized as F-0 through F-24 across six layers:

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
```

Architecture changes must be versioned rather than silently rewriting the meaning of an already-locked version.
