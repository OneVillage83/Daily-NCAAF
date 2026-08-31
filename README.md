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
- **B.2-B broad discovery:** complete for games/PBP, college-native families, the continuous 2015–2026 portal/talent/rating era scan, and the 2023–2026 Team Talent Composite exact-membership audit.
- The observed CFBD transfer-portal coverage floor is **2021**: annual queries returned zero rows through 2020 and substantial coverage from 2021 onward.
- Team Talent Composite membership is season-specific: 2023 contains all 133 FBS teams plus 105 additional programs; 2024 exactly matches all 134 FBS teams; 2025 is an FBS subset missing exactly **Air Force** and **Navy**; 2026 again exactly matches all 138 FBS teams.
- `NO TALENT ROW != ZERO TALENT`; talent rows must be reconciled against canonical program-season membership.
- CORE public retrospective coverage begins in 2016. Elo, SRS, SP+, FPI and CORE retain distinct entity-universe and temporal contracts.
- Temporary HTTP 429 responses are transport states, not missing-data states. Targeted probes use bounded pacing/retry behavior.
- **Positive identity continuity is now empirically verified in the selected cases.** CFBD roster athlete IDs remained stable for Jalen Milroe across four Alabama seasons, Dillon Gabriel across UCF→Oklahoma→Oregon, Travis Hunter across Jackson State FCS→Colorado FBS, and Caleb Downs across Alabama→Ohio State. Their recruiting `athleteId` values directly matched the roster athlete IDs.
- The measured transfer-portal rows for Gabriel, Hunter, and Downs exposed contextual transfer evidence but **no explicit player/athlete identifier**. Portal rows therefore require reconciliation to canonical player identity.
- CFBD coach IDs remained stable across school changes for Nick Saban, Kalen DeBoer, and Curt Cignetti, supporting them as strong provider crosswalks while Daily-NCAAF retains canonical `PERSON -> COACH -> COACH_ROLE_STINT` identity.
- The provider roster field named `year` did not behave as the requested season key in the selected player cases; requested observation season must be stored explicitly rather than inferred from that field.
- **Active B.2-B gate:** recruit-linkage hard cases where recruiting `athleteId` is null, including recovery through roster `recruitIds` and normalized-name collision evidence.
- Historical CFBD lines remain useful market evidence but are **not** timestamped sportsbook quote tape. Daily-Data-Core remains authoritative for sportsbook identity, aliases, quote chronology and no-vig.
- B.2-C cross-provider reconciliation, B.2-D prospective live revision measurement and B.2-E availability-source trials remain before Phase C.

Current references:

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V9.md`](./docs/data/PROVIDER_PROBE_RESULTS_V9.md)
- [`docs/data/CFBD_NATIVE_IDENTITY_SCOPE_PLAN_V1.md`](./docs/data/CFBD_NATIVE_IDENTITY_SCOPE_PLAN_V1.md)
- [`docs/data/CFBD_IDENTITY_CASE_PROBE_SPEC_V1.md`](./docs/data/CFBD_IDENTITY_CASE_PROBE_SPEC_V1.md)
- [`docs/data/CFBD_RECRUIT_LINKAGE_GAP_PROBE_SPEC_V1.md`](./docs/data/CFBD_RECRUIT_LINKAGE_GAP_PROBE_SPEC_V1.md)

Research-only probe tooling:

- [`scripts/probes/provider_coverage_probe.py`](./scripts/probes/provider_coverage_probe.py)
- [`scripts/probes/cfbd_native_family_probe.py`](./scripts/probes/cfbd_native_family_probe.py)
- [`scripts/probes/cfbd_talent_scope_probe.py`](./scripts/probes/cfbd_talent_scope_probe.py)
- [`scripts/probes/cfbd_identity_case_probe.py`](./scripts/probes/cfbd_identity_case_probe.py)
- [`scripts/probes/cfbd_recruit_linkage_gap_probe.py`](./scripts/probes/cfbd_recruit_linkage_gap_probe.py)

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
