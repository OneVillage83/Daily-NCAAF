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
- **B.2-C C2 — Program/team provider crosswalk:** **ACTIVE**.
- **B.2-D — Prospective live revision/PIT capture:** still required.
- **B.2-E — Availability-source trials:** still required.

Production canonical-schema implementation remains intentionally blocked until the Phase B evidence gate is satisfied.

## C1 game/event identity — frozen

Final 2024 V4 evidence:

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
exact shared event IDs                    920
normalized ESPN FBS-involved events      920
normalized exact overlap                  920
normalized CFBD-only                        0
normalized ESPN-only                        0

SAME_SIDE                                 918
SWAPPED_SIDES                               2
UNRESOLVED                                  0
AMBIGUOUS                                   0
counterpart-anchor alignments                2

week MATCH                                920
score MATCH                               919
score UNAVAILABLE                           1
score MISMATCH                              0
lifecycle MATCH                           920

participant observations                 1840
unique CFBD team names                    230
unique ESPN team IDs                      230
team-ID crosswalk conflicts                 0
```

Frozen rules include:

```text
provider home/away side != canonical participant identity
scores are compared only after participant alignment
provider season totals require event-universe normalization
```

Inside an exact-ID matched two-participant event, one independently strong participant alignment may anchor the remaining participant by elimination only when there is no competing opposite-orientation evidence.

The two event-local counterpart-anchor cases were the CFBD `Saint Francis` vs ESPN `St. Francis (PA) Red Flash` games. No global alias was invented.

References:

- [`docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md`](./docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V14.md`](./docs/data/PROVIDER_PROBE_RESULTS_V14.md)

## C2 program/team provider crosswalk — active

C2 now tests whether CFBD team IDs and independently derived ESPN team IDs are the same provider-ID namespace across completed 2023–2025 while preserving canonical Daily-NCAAF `PROGRAM_ID` separately.

It measures:

```text
FBS schedule-crosswalk coverage
CFBD /teams/fbs id == derived ESPN team_id
within-season ID collisions
cross-season provider-ID stability
name evolution on stable provider IDs
FBS membership transitions
```

2026 is intentionally excluded from the completed-season freeze window because the SportsDataverse schedule remains an acquisition-state subset.

References:

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_PLAN_V1.md`](./docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_PLAN_V1.md)
- [`scripts/probes/cross_provider_team_crosswalk_probe.py`](./scripts/probes/cross_provider_team_crosswalk_probe.py)
- [`tests/probes/test_cross_provider_team_crosswalk_probe.py`](./tests/probes/test_cross_provider_team_crosswalk_probe.py)

## Important temporal evidence retained outside C1

The 2024 providers still disagree on kickoff timestamps for 15 events by more than 60 seconds, ranging from minutes to many hours. These remain provider-time semantic observations rather than identity failures.

The 2026 schedule comparison also showed three exact shared games already final in CFBD while the immutable SportsDataverse asset still carried `STATUS_IN_PROGRESS` with intermediate scores.

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
