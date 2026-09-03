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
- **B.2-C C5 — Venue/conference/context reconciliation:** **ACTIVE — C5-A measured/partial, C5-B active**.
- **B.2-D — Prospective live revision/PIT capture:** still required.
- **B.2-E — Availability-source trials:** still required.

Production canonical-schema implementation remains intentionally blocked until the Phase B evidence gate is satisfied.

## Provenance note for B.2-C

Current SportsDataverse build documentation explicitly describes the CFBD `/games` delivery path as ESPN-origin data redistributed through CFBD, while `espn_cfb_schedules` is ESPN-native.

Therefore the reconciliation freezes establish identifier compatibility, coverage behavior, delivery-path differences and safe canonicalization rules. They are **not independent-source corroboration** of the underlying football facts.

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

The user-executed C4 suite passed all 10 tests.

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

All four targeted portal rows had exactly one contextual candidate and a matching measured `transferDate` observation.

```text
Dillon Gabriel  UCF -> Oklahoma       TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Dillon Gabriel  Oklahoma -> Oregon    TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Caleb Downs     Alabama -> Ohio State TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Travis Hunter   Jackson State -> Colorado PARTIAL_DIRECT_SHARED_ID_BRACKET
```

Hunter remains partial because the ESPN-derived 2022 roster contains zero Jackson State rows; that remains an explicit coverage gap rather than an identity conflict.

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

## C5 venue/conference/context reconciliation — active

### C5-A — native schedule context — measured / partial

The user-executed C5-A suite passed all 11 tests and retained 100% CFBD-side exact event coverage across the completed 2023-2025 window.

```text
2023  910 / 910
2024  920 / 920
2025  934 / 934
```

The selected `espn_cfb_schedules` CSVs do **not** expose event `venue_id` or participant conference/division columns. Those V1 states are therefore `UNAVAILABLE`, not disagreements.

Usable C5-A context:

```text
venue display text
2023  EXACT 815  MISMATCH 95
2024  EXACT 830  MISMATCH 90
2025  EXACT 827  MISMATCH 107

neutral-site flag
2023  MATCH 907  MISMATCH 3
2024  MATCH 901  MISMATCH 19
2025  MATCH 925  MISMATCH 9

conference-game flag
2023  MATCH 898  MISMATCH 12
2024  MATCH 909  MISMATCH 11
2025  MATCH 933  MISMATCH 1
```

Venue-name examples demonstrate sponsor/branding/history drift, so display text is not venue identity. Neutral-site disagreements remain provider observations. Conference-game flag mismatches concentrate in special semantic contexts such as championship and independent/Army-Navy cases and remain distinct from conference affiliation.

Locked:

```text
field absent from source artifact != disagreement
UNAVAILABLE != MISMATCH
venue display text != venue identity
conferenceGame != conference_competition semantics by definition
```

References:

- [`docs/data/PROVIDER_PROBE_RESULTS_V19.md`](./docs/data/PROVIDER_PROBE_RESULTS_V19.md)
- [`docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_PLAN_V1.md`](./docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_PLAN_V1.md)

### C5-B — team-season context / home-venue anchor — active

C5-B uses documented ESPN-native fields from the published `espn_cfb_teams` season table for the missing participant context:

```text
team_id
division
conference_*
venue_id
venue_name
```

That table also contains explicitly backported CFBD fields. The C5-B harness whitelists ESPN-native fields and refuses to use `cfbd_conference`, `classification`, or other backported CFBD fields as second-path evidence.

It will compare participant classification and conference through the exact team IDs already established by C1/C2. ESPN team-season `venue_id` is used only as a conservative standard-home-venue anchor; a team home venue is never substituted for direct event venue identity.

Locked distinction:

```text
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
team-season home venue != event venue by definition
CFBD-backported team columns != ESPN-native evidence
```

References:

- [`docs/data/B2C_C5_CONTEXT_FOLLOWUP_PLAN_V1.md`](./docs/data/B2C_C5_CONTEXT_FOLLOWUP_PLAN_V1.md)
- [`scripts/probes/cross_provider_context_reconciliation_probe_v2.py`](./scripts/probes/cross_provider_context_reconciliation_probe_v2.py)
- [`tests/probes/test_cross_provider_context_reconciliation_probe_v2.py`](./tests/probes/test_cross_provider_context_reconciliation_probe_v2.py)

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
