# Daily NCAAF

**The Daily Line — College Football Intelligence Engine**

Daily NCAAF is the college-football-specific prediction, simulation, market-evaluation, and continuous-learning system for The Daily Line.

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
- **B.2-C — CFBD ↔ ESPN/cfbfastR cross-provider reconciliation:** active; C1 game/event identity is at its final V4 counterpart-anchor exit gate.
- **B.2-D — Prospective live revision/PIT capture:** still required.
- **B.2-E — Availability-source trials:** still required.

Production canonical-schema implementation remains intentionally blocked until the Phase B evidence gate is satisfied.

### Locked B.2-B evidence

- CFBD `classification=fbs` is an FBS-involved event universe, not strict FBS-vs-FBS.
- sampled PBP `wallclock` is absent through 2017 and generally available-but-nullable from 2018 onward; it is not publication time.
- PPA nullness is play-family dependent.
- observed transfer-portal coverage begins in 2021; measured portal rows contain transfer context but no explicit player identifier.
- Team Talent Composite scope is season-specific; 2025 is missing exactly Air Force and Navy.
- `NO TALENT ROW != ZERO TALENT`.
- stable CFBD roster athlete IDs survived same-program seasons, multiple transfers and an FCS→FBS move in selected cases.
- stable CFBD coach IDs survived school changes in selected cases.
- direct recruiting `athleteId` linkage is materially incomplete.
- sampled roster `recruitIds` did not directly recover tested missing-`athleteId` recruiting rows.
- normalized-name collisions occurred in every tested recruiting year.
- `NAME MATCH != IDENTITY MATCH`.
- `recruit.committedTo != canonical PLAYER_PROGRAM_STINT`.
- historical CFBD lines are not timestamped sportsbook quote tape; sportsbook identity, quote chronology and no-vig remain owned by `Daily-Data-Core`.

## B.2-C C1 — current evidence

The successful V3 run measured completed 2024 as:

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
exact shared event IDs                    920
normalized ESPN FBS-involved events      920
normalized overlap with CFBD              920
normalized CFBD-only                        0
normalized ESPN-only                        0
```

This is strong empirical evidence that measured CFBD game IDs and SportsDataverse/ESPN `game_id` values share the ESPN event-ID namespace for the complete 2024 FBS-involved universe.

### Provider home/away is not canonical identity

V3 correctly resolved provider-side reversals in:

```text
401677085  UTSA / Coastal Carolina
401677093  USC / Texas A&M
```

After participant alignment, both scores match.

Locked:

```text
same event + same participant set + swapped provider sides != identity conflict
provider home/away side != canonical participant identity
```

### Final V3 edge case

V3 left only two unresolved orientations:

```text
401644732  Kent State vs Saint Francis
401644737  Eastern Michigan vs Saint Francis
```

CFBD calls the opponent `Saint Francis`; ESPN/SportsDataverse calls it `St. Francis (PA) Red Flash`. In both exact-ID events the other participant is independently aligned.

V4 therefore adds a conservative **counterpart-anchor** rule:

```text
EXACT EVENT ID
+ exactly two participants
+ one strong participant alignment
+ no competing opposite-orientation anchor
=> align the remaining participant by elimination
```

This is not a hard-coded alias table and may not override competing identity evidence.

### V3 2024 field agreement

```text
week MATCH                     920
kickoff <= 60 seconds          905
kickoff > 60 seconds            15
lifecycle MATCH                920
score MATCH                    917
score UNAVAILABLE                1
score UNRESOLVED_ORIENTATION     2
score MISMATCH                   0
team crosswalk conflicts         0
```

The 15 kickoff differences remain source-time semantic evidence until scheduled/revised/actual-start meaning is proven.

### 2026 acquisition-state evidence

At V3 acquisition:

```text
CFBD season events                    888
SportsDataverse/ESPN events             8
exact shared event IDs                  8
ESPN-only                                0
```

All eight shared kickoff times matched. Three exact shared games were already final in CFBD while the immutable SportsDataverse artifact still contained `STATUS_IN_PROGRESS` and intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

### Active C1 V4 references

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V13.md`](./docs/data/PROVIDER_PROBE_RESULTS_V13.md)
- [`docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V3.md`](./docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V3.md)
- [`scripts/probes/cross_provider_game_reconciliation_probe_v4.py`](./scripts/probes/cross_provider_game_reconciliation_probe_v4.py)
- [`tests/probes/test_cross_provider_game_reconciliation_probe_v4.py`](./tests/probes/test_cross_provider_game_reconciliation_probe_v4.py)

If V4 resolves the two Saint Francis cases with explicit counterpart-anchor evidence while preserving 920/920 normalized event overlap and zero team-ID conflicts, **C1 can freeze**. Work then advances to **C2 program/team provider crosswalk freeze** and **C3 player cross-provider reconciliation**.

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
