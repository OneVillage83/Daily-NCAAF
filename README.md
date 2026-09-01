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

**Phase B — Source, Coverage, PIT & Reconciliation Audit** is active.

- **B.1 — Public Source & Contract Audit:** complete.
- **B.2-A — CFBD games/PBP representative audit:** core complete.
- **B.2-B — CFBD college-native family, era, scope and identity audit:** complete.
- **B.2-C — CFBD ↔ ESPN/cfbfastR cross-provider reconciliation:** active; C1 game identity is at its final participant-alignment correction gate.
- B.2-D prospective live revision/PIT capture and B.2-E availability-source trials remain before production canonical-schema implementation is unlocked.

### Locked B.2-B evidence

- CFBD `classification=fbs` is an FBS-involved event universe, not strict FBS-vs-FBS.
- sampled PBP `wallclock` is absent through 2017 and generally available-but-nullable from 2018 onward; it is not publication time.
- PPA nullness is play-family dependent.
- observed transfer-portal coverage begins in 2021; measured portal rows contain transfer context but no explicit player identifier.
- Team Talent Composite scope is season-specific; 2025 is missing exactly Air Force and Navy.
- `NO TALENT ROW != ZERO TALENT`.
- stable CFBD roster athlete IDs survived same-program seasons, multiple FBS transfers and an FCS→FBS move in selected cases.
- stable CFBD coach IDs survived school changes in selected cases.
- direct recruiting `athleteId` linkage is materially incomplete.
- sampled roster `recruitIds` did not directly recover the tested missing-`athleteId` recruiting rows.
- normalized-name collisions occurred in every tested recruiting year.
- `NAME MATCH != IDENTITY MATCH`.
- `recruit.committedTo != canonical PLAYER_PROGRAM_STINT`.
- historical CFBD lines are not timestamped sportsbook quote tape; sportsbook identity/quote chronology/no-vig remain owned by `Daily-Data-Core`.

### B.2-C C1 — major result

The corrected V2 2024 comparison measured:

```text
CFBD FBS-involved events              920
SportsDataverse/ESPN events           966
exact shared event IDs                 920
CFBD-only raw IDs                        0
normalized ESPN FBS-involved events   920
normalized ESPN-only events              0
```

That is strong evidence that measured CFBD game IDs and SportsDataverse/ESPN `game_id` values share the ESPN event-ID namespace for the complete 2024 FBS-involved universe.

Two apparent V2 score mismatches and four team-ID conflicts were traced to **provider home/away side swaps** in two bowl games, not score or identity disagreement:

```text
401677085  UTSA / Coastal Carolina
401677093  USC / Texas A&M
```

Locked:

```text
same event + same participant set + swapped provider sides != identity conflict
home/away label != canonical participant identity
```

The final C1 V3 probe therefore aligns participants inside the exact-ID-matched event before comparing scores or deriving team-ID crosswalks.

### 2024 temporal evidence

```text
week agreement          920 / 920
kickoff <= 60s          905 / 920
kickoff > 60s            15 / 920
lifecycle agreement     920 / 920
```

Kickoff disagreement is retained as source-time evidence until scheduled/revised/actual-start semantics are established. It is not automatically treated as bad data.

### 2026 current-state evidence

At the V2 acquisition, CFBD exposed 888 season events while the exact downloaded SportsDataverse schedule asset contained only 8. All eight SportsDataverse event IDs existed in CFBD and all eight kickoff times matched.

Three matched games had already reached final state in CFBD while the downloaded SportsDataverse asset still contained `STATUS_IN_PROGRESS` and intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source asset hash + acquired_at are mandatory
```

The SportsDataverse release is also actively regenerating assets during this audit. V3 therefore selects the **newest supported season asset from the manifest**, using file format only as a timestamp tie-breaker.

### Active C1 V3 tooling

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V12.md`](./docs/data/PROVIDER_PROBE_RESULTS_V12.md)
- [`docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md`](./docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md)
- [`docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V2.md`](./docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V2.md)
- [`scripts/probes/cross_provider_game_reconciliation_probe_v3.py`](./scripts/probes/cross_provider_game_reconciliation_probe_v3.py)
- [`tests/probes/test_cross_provider_game_reconciliation_probe_v3.py`](./tests/probes/test_cross_provider_game_reconciliation_probe_v3.py)

C1 can close if the V3 2024 run preserves complete normalized event overlap while eliminating the side-swap artifacts and leaving no unexplained team-ID conflict. Then work advances to **C2 program/team crosswalk freeze** and **C3 player reconciliation**.

Production canonical-schema implementation remains intentionally blocked until B.2-C/B.2-D/B.2-E provide enough evidence for provider-independent contracts.

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
