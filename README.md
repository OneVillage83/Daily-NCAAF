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
- **B.2-C C3-A — Targeted player cross-provider identity:** **COMPLETE**.
- **B.2-C C3-B — Player breadth/coverage reconciliation:** **ACTIVE**.
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

Provider home/away side is not canonical identity. Scores are compared only after participant alignment. Event-universe normalization precedes provider season-count comparison.

References:

- [`docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md`](./docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V14.md`](./docs/data/PROVIDER_PROBE_RESULTS_V14.md)

## C2 program/team provider crosswalk — frozen

Completed 2023-2025 measured 100% FBS schedule-derived team crosswalk coverage and exact direct external-ID equality in every program-season:

```text
2023  133 / 133 direct CFBD-ID == ESPN-ID matches
2024  134 / 134 direct CFBD-ID == ESPN-ID matches
2025  136 / 136 direct CFBD-ID == ESPN-ID matches
```

Cross-season:

```text
136 unique FBS school names
136 unique CFBD team IDs
136 unique ESPN team IDs
0 same-school multi-ID cases
0 reverse-ID collisions
```

Measured membership transitions remain program state, not identity replacement:

```text
2024: Kennesaw State enters FBS
2025: Delaware and Missouri State enter FBS
```

The audited CFBD and ESPN-derived sources expose the same numeric external team-ID namespace over the measured window, but that external value never becomes canonical Daily-NCAAF `PROGRAM_ID`.

References:

- [`docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md`](./docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V15.md`](./docs/data/PROVIDER_PROBE_RESULTS_V15.md)

## C3 player cross-provider identity — active

### C3-A targeted identity — complete

The user-executed C3-A suite passed all 11 tests.

Target continuity results:

```text
Jalen Milroe 4432734
  Alabama 2023     DIRECT_SHARED_PROVIDER_ID
  Alabama 2024     DIRECT_SHARED_PROVIDER_ID

Dillon Gabriel 4427238
  Oklahoma 2022    DIRECT_SHARED_PROVIDER_ID
  Oklahoma 2023    DIRECT_SHARED_PROVIDER_ID
  Oregon 2024      DIRECT_SHARED_PROVIDER_ID

Caleb Downs 4870706
  Alabama 2023     DIRECT_SHARED_PROVIDER_ID
  Ohio State 2024  DIRECT_SHARED_PROVIDER_ID
  Ohio State 2025  DIRECT_SHARED_PROVIDER_ID

Travis Hunter 4685415
  Jackson State 2022  CFBD_ONLY_IDENTIFIER
  Colorado 2023       DIRECT_SHARED_PROVIDER_ID
  Colorado 2024       DIRECT_SHARED_PROVIDER_ID
```

Hunter's 2022 result is a source-coverage gap: the SportsDataverse roster asset contained zero Jackson State rows, so it is not an athlete-ID disagreement.

Across the nine measured FBS roster slices:

```text
CFBD unique athlete IDs        1111
ESPN unique athlete IDs        1111
exact shared athlete IDs       1099
CFBD-only IDs                    12
ESPN-only IDs                    12
weighted exact-ID overlap     98.92% / 98.92%
duplicate-ID slices              0
```

This strongly supports a shared recent-FBS external athlete-ID namespace while separately proving that roster coverage is not perfectly identical.

Same-ID display-name differences were common enough to reinforce:

```text
name inequality != identity break
name matching remains diagnostic only
```

References:

- [`docs/data/PROVIDER_PROBE_RESULTS_V16.md`](./docs/data/PROVIDER_PROBE_RESULTS_V16.md)
- [`docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_PLAN_V1.md`](./docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_PLAN_V1.md)
- [`scripts/probes/cross_provider_player_identity_probe.py`](./scripts/probes/cross_provider_player_identity_probe.py)

### C3-B breadth / coverage — active

Before freezing C3 globally, a deterministic 13-slice breadth pass tests whether the C3-A overlap generalizes across conference, independent, service-academy, realignment and recent-FBS-entry contexts.

```text
2024: Clemson, Michigan, Utah, Georgia, Army, Kennesaw State,
      Toledo, Boise State, App State, Oregon State, Notre Dame
2025: Delaware, Missouri State
```

References:

- [`docs/data/B2C_C3_PLAYER_COVERAGE_BREADTH_PLAN_V1.md`](./docs/data/B2C_C3_PLAYER_COVERAGE_BREADTH_PLAN_V1.md)
- [`scripts/probes/cross_provider_player_coverage_probe.py`](./scripts/probes/cross_provider_player_coverage_probe.py)
- [`tests/probes/test_cross_provider_player_coverage_probe.py`](./tests/probes/test_cross_provider_player_coverage_probe.py)

C3 freeze will be an identity/crosswalk freeze, not a claim that either provider roster is population-complete.

## Temporal evidence retained outside identity freezes

The 2024 providers still disagree on kickoff timestamps for 15 events by more than 60 seconds. These remain provider-time semantic observations rather than identity failures.

The 2026 comparison also showed exact shared games already final in CFBD while the immutable SportsDataverse schedule asset still carried `STATUS_IN_PROGRESS` with intermediate scores.

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
