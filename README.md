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
- **B.2-C C4 — Transfer-event reconciliation:** **COMPLETE / FROZEN**.
- **B.2-C C5 — Venue/conference/context reconciliation:** **COMPLETE / FROZEN**.
- **B.2-C C6 — Selected play-level reconciliation:** **ACTIVE**.
- **B.2-D — Prospective live revision/PIT capture:** still required.
- **B.2-E — Availability-source trials:** still required.

Production canonical-schema implementation remains intentionally blocked until the Phase B evidence gate is satisfied.

## Provenance note for B.2-C

Current SportsDataverse/cfbfastR build documentation shows that CFBD and ESPN delivery paths may share ESPN-origin upstream data. Reconciliation freezes therefore establish identifier compatibility, coverage behavior, delivery-path differences and safe canonicalization rules. They are **not independent-source corroboration** of the underlying football facts.

See:

- [`docs/data/B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md`](./docs/data/B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md)

## C1 game/event identity — frozen

Completed 2024 demonstrated complete normalized FBS event overlap with zero unexplained identity conflicts.

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

External provider team IDs never become canonical Daily-NCAAF `PROGRAM_ID` values.

## C3 player cross-provider identity — frozen

Across the 22 measured FBS team-season slices:

```text
CFBD athlete-ID observations       2745
ESPN athlete-ID observations       2749
exact shared observations          2715
combined weighted CFBD overlap   98.9071%
combined weighted ESPN overlap   98.7632%
```

Frozen:

```text
shared external athlete ID = strong provider-crosswalk identity evidence
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
name inequality != identity break
```

## C4 transfer-event reconciliation — frozen

Final states:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

Frozen:

```text
portal row != PLAYER identity
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
transferDate != publication time
transferDate != acquired_at
```

References:

- [`docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_FREEZE_V1.md`](./docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V18.md`](./docs/data/PROVIDER_PROBE_RESULTS_V18.md)

## C5 venue/conference/context reconciliation — frozen

C5 closed after four bounded passes across completed 2023-2025.

Exact event coverage remained complete from the CFBD side:

```text
2023  910 / 910
2024  920 / 920
2025  934 / 934
```

All aligned participant external team IDs and division/classification labels matched, and no referenced team metadata was missing.

C5-A established that absent schedule columns remain unavailable rather than mismatches. C5-B established that team-season home-venue metadata is not event-venue truth. C5-C added only measured explicit conference-name equivalence. C5-D exhaustively classified every residual conference difference.

Final C5-D result:

```text
CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       37
TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
UNCLASSIFIED                                    0
```

Frozen:

```text
FIELD ABSENT != MISMATCH
UNAVAILABLE != CONTRADICTORY DATA
provider display label != canonical identity
venue display text != venue identity
TEAM_SEASON_HOME_VENUE_OBSERVATION != GAME_VENUE_OBSERVATION
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
provider neutral-site flag != canonical truth by default
conferenceGame != conference_competition semantics by definition
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
TEAM-SEASON CONFERENCE METADATA != guaranteed historical affiliation truth
provider conference ID != canonical CONFERENCE_ID
provider venue ID != canonical VENUE_ID
```

References:

- [`docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_FREEZE_V1.md`](./docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_FREEZE_V1.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V22.md`](./docs/data/PROVIDER_PROBE_RESULTS_V22.md)

## C6 selected play-level reconciliation — active

C6-A starts with exact play-ID compatibility before attempting any semantic alignment.

Selected already-reconciled event IDs span 2023-2025 and include regular-season, FBS-v-FCS and the two 2024 postseason side-swap cases.

Second delivery path:

```text
ESPN site-v2 game summary play-by-play
```

CFBD historical `/plays` requires year/week, so the probe resolves each game with `/games?id=...`, fetches the corresponding FBS-involved week/seasonType play universe, then filters locally to the exact frozen game ID.

Per game C6-A measures:

```text
cfbd_unique_play_ids
espn_unique_play_ids
exact_shared_play_ids
cfbd_only_play_ids
espn_only_play_ids
exact-ID overlap rates
duplicate play IDs
```

Only exact shared play IDs are then compared on:

```text
period
clock seconds
down
distance
yards to goal
scoring flag
play type text
play text
```

Provider-only rows remain explicit. No row-order, clock-only or text-only force matching is allowed in C6-A.

If exact play-ID overlap is insufficient, a bounded C6-B composite-alignment study will be added rather than weakening the identity contract.

References:

- [`docs/data/B2C_C6_SELECTED_PLAY_RECONCILIATION_PLAN_V1.md`](./docs/data/B2C_C6_SELECTED_PLAY_RECONCILIATION_PLAN_V1.md)
- [`scripts/probes/cross_provider_play_reconciliation_probe.py`](./scripts/probes/cross_provider_play_reconciliation_probe.py)
- [`tests/probes/test_cross_provider_play_reconciliation_probe.py`](./tests/probes/test_cross_provider_play_reconciliation_probe.py)

## Temporal evidence retained outside reconciliation freezes

The 2024 delivery paths disagree on kickoff timestamps for 15 events by more than 60 seconds. These remain provider-time semantic observations rather than identity failures.

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
