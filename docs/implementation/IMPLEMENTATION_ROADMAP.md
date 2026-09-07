# Daily NCAAF Implementation Roadmap

**Status: ACTIVE PLANNING CONTRACT**

This roadmap translates the locked F00-F24 architecture into implementation order. It is intentionally dependency-driven: later modeling work should not outrun evidence, identity, point-in-time, or feature-contract foundations.

## Phase A — Repository & Engineering Foundation

Goals:

- Python/package/tooling baseline
- test/lint/type-check configuration
- configuration/secrets pattern
- structured logging
- migration framework
- local data directories and ignore rules
- run/job lifecycle primitives
- architecture-aware CI

Exit criteria:

- repository installs reproducibly;
- lint/type/tests run from documented commands;
- no secrets or mutable local data committed;
- first migration can initialize a clean database.

## Phase B — Source & Coverage Audit

Goals:

- provider capability registry
- historical coverage matrix
- season/field/entity coverage
- live-update capability inventory
- licensing/attribution metadata
- PIT-fidelity classification
- provider reliability/fallback plan

Key deliverables:

- `docs/data/PROVIDER_REGISTRY.md`
- `docs/data/SOURCE_COVERAGE_MATRIX.md`
- `docs/data/PIT_AVAILABILITY_MATRIX.md`

Do not begin serious historical model training until the major source eras are understood.

## Phase C — Canonical Domain Schema

Implement versioned entities/contracts for:

- competition/classification
- school/program/program-season
- conference/conference affiliation
- season/phase/week
- venue
- game/result separation
- person/player/player-program stint
- coach/coach-program-role stint
- roster/eligibility state
- provider crosswalks

Exit criteria:

- core identities can be represented without provider-specific primary keys;
- conference realignment and transfers are historically expressible;
- final result data is structurally separable from pregame state.

## Phase D — Raw Evidence & Provenance

Goals:

- immutable raw artifact store
- checksums/content addressing
- acquisition metadata
- retry/failure capture
- provider adapters behind interfaces
- normalization boundaries

Exit criteria:

- every normalized test record can be traced to raw evidence;
- repeated acquisition is idempotent where expected;
- provider schema changes do not leak directly into models.

## Phase E — Identity & Reconciliation

Goals:

- program/provider crosswalks
- player identity across transfers/jersey/position changes
- coach identity/role stints
- game reconciliation
- ambiguity/confidence records

Exit criteria:

- transfer cases preserve one canonical player;
- schedule revisions do not create duplicate canonical games;
- ambiguous matches surface instead of being silently guessed.

## Phase F — Historical PIT Foundation

Goals:

- timestamp semantics
- native/reconstructable/retrospective/unknown PIT classification
- immutable observation revisions
- historical as-of queries
- prediction-snapshot primitives
- leakage tests

Exit criteria:

- historical query can reconstruct what was defensibly knowable at T;
- post-kickoff/final-result leakage tests fail closed;
- later-known starter/transfer/availability state cannot backfill earlier snapshots.

## Phase G — Play / Drive Normalization

Goals:

- canonical game/possession/drive/play/event hierarchy
- `PLAY_EXECUTION` taxonomy
- design modifiers
- penalty/turnover/special-teams semantics
- pre-snap/post-snap separation
- ruleset association
- participation confidence
- low-leverage/reserve context

## Phase H — Football State Engines

Implement progressively:

1. Program/Team State
2. Player State
3. Unit State
4. Coaching/Scheme State
5. Injury/Availability State
6. Weather/Venue/Home Context
7. Travel/Rest/Recovery

Exit criteria:

- every state is time-indexed;
- uncertainty can be represented;
- opponent adjustment is built into team-performance interpretation;
- availability scenarios can propagate to units.

## Phase I — Feature Registry & Historical Snapshots

Goals:

- feature registry
- feature contracts
- grain definitions
- PIT eligibility
- missingness/imputation policies
- feature eras
- dependency graph
- immutable feature snapshots

Exit criteria:

- no model-ready feature exists without a contract;
- market features cannot enter football-only models accidentally;
- feature snapshots can be reproduced from lineage.

## Phase J — Baseline Modeling

Implement and retain controls:

- naive baseline
- Elo/SRS-like model
- opponent-adjusted efficiency
- offense/defense score model
- gradient-boosted game model
- hierarchical college model
- early-season roster/talent transition baseline
- market-only benchmark

Use chronological evaluation from the beginning.

## Phase K — Advanced Models

Candidate workstreams:

- dynamic state-space models
- hierarchical Bayesian models
- player/unit aggregation
- matchup interactions
- graph/network schedule models
- sequence models
- advanced ensembles
- dynamic offseason roster transition model

Every advanced family enters challenger status first.

## Phase L — Simulation

Progression:

```text
Score distributions
  ↓
Drive simulation
  ↓
Play simulation
  ↓
Player/unit conditioned simulation
  ↓
World-model research
```

Support scenario mixtures for unresolved availability.

## Phase M — Market / Value / Recommendation

Integrate Daily Data Core for:

- sportsbook quotes
- opening/current/closing market
- consensus/no-vig
- movement/dispersion

Daily NCAAF adds:

- football-only fair price
- market-only benchmark
- market-aware models
- ensemble
- edge/EV
- uncertainty/risk
- Recommendation Gate

Every supported market prediction exists before BET/LEAN/PASS/AVOID.

## Phase N — Reporting / Publication

Goals:

- complete daily game coverage
- ranked opportunities
- transparent model/gate provenance
- uncertainty/reason codes
- report/API/export contracts
- The Daily Line publication integration

Publication must not mutate historical prediction records.

## Phase O — Settlement / Evaluation / Continuous Learning

Goals:

- football result ledger
- market settlement ledger
- model performance ledger
- closing-line capture
- calibration reports
- CLV/ROI reports
- Gate-effectiveness analysis
- provider-quality monitoring
- drift monitoring
- retraining policies
- champion/challenger promotion
- negative-result register

## Phase P — Shared Football Extraction

Only after Daily NFL and Daily NCAAF implementations exist:

- compare duplicate concepts;
- identify semantically identical contracts;
- extract proven shared components;
- leave sport-specific behavior in sport repositories;
- prefer composition/interfaces over deep inheritance.

## Phase Q — College Football World Model Research

Long-term research into probabilistic state transitions across player, unit, program, matchup, play, drive, and game state.

World-model work never bypasses PIT correctness, reproducibility, calibration, or simpler-model controls.

---

# Roadmap rule

A later phase may be researched early in isolation, but production dependency order must not be inverted. For example, experimental model notebooks may exist before the complete live system, but no model is treated as production-valid until its evidence, PIT, feature, evaluation, and lineage contracts are satisfied.
