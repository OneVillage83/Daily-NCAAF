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
- **B.2-B — CFBD college-native family, era, scope and identity audit:** **complete**.
- **B.2-C — CFBD ↔ ESPN/cfbfastR cross-provider reconciliation:** **active**.
- B.2-D prospective live revision/PIT capture and B.2-E availability-source trials remain before production canonical-schema implementation is unlocked.

### Locked B.2-B evidence

- CFBD `classification=fbs` is an FBS-involved event universe, not strict FBS-vs-FBS.
- sampled PBP `wallclock` is absent through 2017 and generally available-but-nullable from 2018 onward; it is not publication time.
- PPA nullness is play-family dependent.
- the 2024 Liberty-at-App-State incomplete game is a real Hurricane Helene cancellation.
- observed CFBD transfer-portal coverage begins in 2021; portal rows contain useful transfer context but no explicit player identifier in the measured cases.
- Team Talent Composite scope is season-specific: 2023 contains all FBS teams plus 105 extras; 2024 exactly matches FBS; 2025 is missing exactly Air Force and Navy; 2026 again exactly matches FBS.
- `NO TALENT ROW != ZERO TALENT`.
- CORE public retrospective history begins in 2016; Elo/SRS/SP+/FPI/CORE retain separate entity-universe and PIT contracts.
- historical CFBD lines are not timestamped sportsbook quote tape; sportsbook identity, quote chronology and no-vig remain owned by `Daily-Data-Core`.
- stable CFBD roster athlete IDs survived same-program seasons, multiple FBS transfers, and an FCS→FBS move in the measured Jalen Milroe, Dillon Gabriel, Travis Hunter and Caleb Downs cases.
- stable CFBD coach IDs survived school changes for Nick Saban, Kalen DeBoer and Curt Cignetti.
- direct recruiting `athleteId` linkage is materially incomplete.
- across 12 sampled missing-`athleteId` recruits, zero roster `recruitIds` lists directly contained the tested recruiting-record ID; eight cases produced only a stable same-name roster candidate and four remained unresolved.
- normalized-name collisions occurred in every tested recruiting year, including a case with the same normalized name, school and position on two distinct recruiting records.
- `NAME MATCH != IDENTITY MATCH`.
- `recruit.committedTo != canonical PLAYER_PROGRAM_STINT`.
- provider roster field `year` cannot be assumed to equal requested roster season.
- HTTP 429 is a transport/rate state, not a missing-data state.

### Active B.2-C work

The first cross-provider pass reconciles CFBD games against the public SportsDataverse `espn_cfb_schedules` release for 2024 and 2026.

The schedule source defines `game_id` as the ESPN event identifier, so the harness tests exact game-ID equality empirically and then measures matched team/week/kickoff/score/lifecycle agreement.

Raw ESPN-only events are retained as **event-universe differences** until classification scope is normalized; they are not automatically labeled CFBD omissions.

Current B.2-C references:

- [`docs/implementation/CURRENT_PHASE.md`](./docs/implementation/CURRENT_PHASE.md)
- [`docs/data/PROVIDER_PROBE_RESULTS_V10.md`](./docs/data/PROVIDER_PROBE_RESULTS_V10.md)
- [`docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md`](./docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md)
- [`scripts/probes/cross_provider_game_reconciliation_probe.py`](./scripts/probes/cross_provider_game_reconciliation_probe.py)
- [`tests/probes/test_cross_provider_game_reconciliation_probe.py`](./tests/probes/test_cross_provider_game_reconciliation_probe.py)

Research-only historical probe tooling remains under `scripts/probes/` and `tests/probes/`.

Production canonical-schema implementation remains intentionally blocked until B.2-C/B.2-D/B.2-E produce enough evidence for provider-independent contracts.

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
