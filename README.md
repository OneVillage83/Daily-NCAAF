# Daily NCAAF

**The Daily Line — College Football Intelligence Engine**

Daily NCAAF is the college-football-specific prediction, simulation, market-evaluation and continuous-learning system for The Daily Line.

The repository is being built as a full production architecture from the beginning rather than as a disposable MVP. Architecture and evidence contracts are documented before implementation so source semantics, identity, point-in-time rules and evaluation assumptions cannot silently drift.

## Core operating rules

- Predict every eligible supported game and market.
- Apply BET / LEAN / PASS / AVOID only after prediction, fair-price, edge, uncertainty and risk evaluation.
- Store, settle and evaluate PASS and AVOID alongside BET and LEAN.
- Enforce historical point-in-time eligibility: information must be defensibly available at or before the prediction snapshot and before kickoff.
- Continue monitoring meaningful pregame information through kickoff.
- Preserve immutable raw evidence before normalization and feature engineering.
- Use canonical internal identities; provider IDs remain crosswalks.
- Keep football-only, market-only, market-aware and ensemble forecasts explicitly distinguishable.
- Use chronological / walk-forward evaluation as the primary validation framework.
- Treat uncertainty as a first-class model output.
- Preserve reproducibility and lineage for published predictions.
- Keep cross-sport infrastructure in `Daily-Data-Core` and college-football-native intelligence in `Daily-NCAAF`.
- Do not prematurely extract shared NFL/NCAAF code; extract only after both implementations prove semantics are truly shared.

## Current phase

**Phase B — Source, Coverage, PIT & Reconciliation Audit** is active.

- **B.1 — Public Source & Contract Audit:** complete.
- **B.2-A — CFBD games/PBP representative audit:** core complete.
- **B.2-B — CFBD college-native family, era, scope and identity audit:** complete.
- **B.2-C C1 — Game/event reconciliation:** **COMPLETE / FROZEN**.
- **B.2-C C2 — Program/team provider crosswalk:** **COMPLETE / FROZEN**.
- **B.2-C C3 — Player cross-provider identity:** **COMPLETE / FROZEN**.
- **B.2-C C4 — Transfer-event reconciliation:** **ACTIVE**.
- **B.2-D — Prospective live revision/PIT capture:** still required.
- **B.2-E — Availability-source trials:** still required.

Production canonical-schema implementation remains intentionally blocked until the Phase B evidence gate is satisfied.

## C1 game/event identity — frozen

Completed 2024 demonstrated complete normalized FBS event overlap across CFBD and ESPN/SportsDataverse with zero unexplained identity conflicts.

```text
exact shared event IDs        920
normalized overlap            920 / 920
normalized provider-only        0 / 0
SAME_SIDE                     918
SWAPPED_SIDES                   2
UNRESOLVED                      0
AMBIGUOUS                       0
score MATCH                   919
score UNAVAILABLE               1
score MISMATCH                  0
```

Provider home/away side is not canonical identity. Scores are compared only after participant alignment.

## C2 program/team provider crosswalk — frozen

Completed 2023-2025 measured 100% FBS schedule-derived team crosswalk coverage and exact direct external-ID equality in every program-season:

```text
2023  133 / 133
2024  134 / 134
2025  136 / 136
```

The audited CFBD and ESPN-derived sources expose the same numeric external team-ID namespace over the measured window, but that value never becomes canonical Daily-NCAAF `PROGRAM_ID`.

## C3 player cross-provider identity — frozen

C3-A targeted transfer/same-program continuity plus C3-B's deterministic breadth sample establish a dominant shared recent-FBS external athlete-ID namespace while keeping roster coverage separate from identity.

Across the 22 measured FBS team-season slices:

```text
CFBD athlete-ID observations       2745
ESPN athlete-ID observations       2749
exact shared observations          2715
combined weighted CFBD overlap   98.9071%
combined weighted ESPN overlap   98.7632%
```

C3-B alone measured:

```text
13 non-empty FBS slices
4 complete exact-set matches
7 high-overlap slices
2 partial-overlap slices
0 zero-team-row slices
0 duplicate-ID slices
```

The weakest provider-side coverage observations were Georgia 2024 from the CFBD side and Utah 2024 from the ESPN side. They remained coverage differences rather than contradictory same-ID mappings.

Frozen:

```text
shared external athlete ID = strong provider-crosswalk identity evidence
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
name inequality != identity break
shared cross-provider ID != historical PIT safety
```

Target transfer continuity included Dillon Gabriel and Caleb Downs with the same direct shared athlete IDs before and after FBS program changes. Travis Hunter's 2022 Jackson State SportsDataverse roster remains a documented source-coverage gap rather than an identity conflict.

References:

- [`docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md`](./docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V16.md`](./docs/data/PROVIDER_PROBE_RESULTS_V16.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V17.md`](./docs/data/PROVIDER_PROBE_RESULTS_V17.md)

## C4 transfer-event reconciliation — active

C4 now reconciles identifier-less CFBD portal observations against the frozen C2 program and C3 player identities plus surrounding CFBD/ESPN roster stints.

Initial events:

```text
Dillon Gabriel  UCF 2021 -> Oklahoma 2022
Dillon Gabriel  Oklahoma 2023 -> Oregon 2024
Travis Hunter   Jackson State 2022 -> Colorado 2023
Caleb Downs     Alabama 2023 -> Ohio State 2024
```

The portal row itself is contextual evidence, not identity authority.

```text
portal name match != PLAYER identity
portal origin/destination != canonical stint by itself
transferDate != publication time
```

References:

- [`docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_PLAN_V1.md`](./docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_PLAN_V1.md)
- [`scripts/probes/cross_provider_transfer_event_probe.py`](./scripts/probes/cross_provider_transfer_event_probe.py)
- [`tests/probes/test_cross_provider_transfer_event_probe.py`](./tests/probes/test_cross_provider_transfer_event_probe.py)

## Temporal evidence retained outside identity freezes

The 2024 providers still disagree on kickoff timestamps for 15 events by more than 60 seconds. These remain provider-time semantic observations rather than identity failures.

The 2026 comparison also showed exact shared games already final in CFBD while an immutable SportsDataverse schedule asset still carried `STATUS_IN_PROGRESS` with intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

## Architecture

The governing architecture lives in [`docs/architecture`](./docs/architecture) and is organized as F-0 through F-24 across six layers:

```text
LAYER 1 — TRUTH & EVIDENCE
F-0 -> F-5

LAYER 2 — FOOTBALL STATE
F-6 -> F-12

LAYER 3 — FEATURES & TARGETS
F-13 -> F-14

LAYER 4 — MODELING & SIMULATION
F-15 -> F-17

LAYER 5 — MARKET / RECOMMENDATION / LEARNING
F-18 -> F-21

LAYER 6 — NCAAF EXTENSIONS & FUTURE RESEARCH
F-22 -> F-24
```

Architecture changes must be versioned rather than silently rewriting the meaning of an already-locked version.
