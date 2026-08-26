# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B public-source documentation audit complete. Empirical coverage/PIT validation is now the active subphase; implementation remains intentionally blocked until that evidence is recorded.

## Active phase

### Phase B — Source & Coverage Audit

#### B.1 — Public Source & Contract Audit — COMPLETE

Completed on 2026-08-26:

- provider/candidate registry;
- source-family coverage matrix;
- historical PIT availability matrix;
- canonical identity/reconciliation rules;
- ruleset/competition-era registry;
- license/commercial-role review at documentation level;
- provider overlap/gap analysis;
- Daily-Data-Core ownership boundary confirmation.

Phase B documents:

- `docs/data/PROVIDER_REGISTRY.md`
- `docs/data/SOURCE_COVERAGE_MATRIX.md`
- `docs/data/PIT_AVAILABILITY_MATRIX.md`
- `docs/data/IDENTITY_RULES.md`
- `docs/data/RULESET_ERAS.md`

### B.2 — Empirical Coverage & PIT Probe — ACTIVE / NEXT

Public documentation tells us what providers claim/expose. It does not establish exact season completeness, field null rates, provider-ID stability, revision behavior, historical availability timestamps or live latency.

The next task is therefore to empirically probe the candidate source stack before Phase C schema design.

## Locked provider direction from B.1

### Adopt / integrate

- **CollegeFootballData (CFBD):** P0 college-native historical foundation and live candidate.
- **SportsDataverse / cfbfastR CFB pipeline:** P0/P1 independent PBP/roster/participant reconciliation and research corpus.
- **NCAA official sources:** rules/stat/result reference and reconciliation.
- **College Football Playoff official sources:** postseason-format/competition truth.
- **Official conference/program availability reports:** required multi-source injury/availability evidence family.
- **Daily-Data-Core:** required shared owner of odds, weather, venue/geospatial primitives, travel/rest primitives, generic provenance, run lifecycle and settlement.

### Trial before adoption

- **SportsDataIO NCAA Football:** priority commercial trial for injury/availability coverage.
- **Sportradar NCAA Football:** commercial trial for live/event/roster redundancy and change-log semantics.

## Major gaps explicitly preserved

1. uniform national historical injury/availability timeline;
2. uniform historical published depth charts;
3. complete OC/DC/play-caller history;
4. complete redshirt/eligibility history;
5. exact timestamped historical sportsbook quote tape in sport repo — belongs in `Daily-Data-Core`;
6. exact historical publication/revision timing for several otherwise-rich historical provider datasets.

These are architecture inputs, not reasons to fake completeness.

## Governing PIT finding

Historical data is not automatically historical knowledge state.

Examples:

- final season aggregates cannot predict earlier games;
- a current API response describing an old roster does not prove when that roster state became available;
- a transfer `transferDate` is not automatically a publication timestamp;
- actual game participation is postgame truth, not pregame expected participation;
- final historical weather is not a historical forecast;
- closing market data cannot be inserted into an earlier snapshot;
- CFBD explicitly documents historical CORE ratings as retrospective methodology output.

Unknown availability defaults to **unavailable for historical pregame use** until a reconstruction rule is justified.

## B.2 empirical probe objectives

For representative providers/endpoints/seasons, record:

1. earliest and latest usable season;
2. row/entity counts;
3. expected-vs-observed game/team/player coverage;
4. key/field null rates;
5. duplicate rates;
6. FBS/FCS and postseason behavior;
7. provider-ID stability across seasons/transfers/revisions;
8. cross-provider game/player/play match rates;
9. schema/version variation by era;
10. timestamp semantics;
11. update latency for live/current sources where accessible;
12. corrections/revision behavior;
13. raw checksums/sample evidence;
14. commercial trial gaps that cannot be tested without provider credentials.

Representative seasons initially include:

```text
2004, 2006, 2010, 2014, 2015, 2016, 2018,
2019, 2020, 2021, 2023, 2024, 2025, 2026
```

The probe must include FBS, FCS, FBS-vs-FCS, independent programs, conference realignment, neutral sites, postseason games, transfers and coaching changes.

## Explicitly not started yet

- production database schema;
- production provider ingestion code;
- broad historical backfill;
- feature engineering;
- model training;
- simulation;
- Recommendation Gate implementation.

Small disposable probe scripts/data are permitted only to measure provider behavior. They must not silently become the production acquisition architecture.

## Phase transition rule

Phase B closes only when:

1. the major source families required for F-0 through F-14 have documented and empirically measured coverage characteristics where access permits;
2. known inaccessible/commercial families are explicitly marked credential/trial-gated rather than guessed;
3. major PIT/revision semantics have validated classifications or conservative exclusion rules;
4. identity probe cases demonstrate an acceptable reconciliation strategy;
5. the remaining gaps are precise enough that Phase C can design canonical contracts around them without depending on one provider schema.

Only then may the project advance to **Phase C — Canonical Schema & Identity Foundation**.
