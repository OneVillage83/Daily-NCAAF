# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT probe is active, with the public SportsDataverse/cfbfastR measurement pass and reproducible probe harness now implemented. Phase C remains intentionally blocked pending authenticated CFBD and cross-provider evidence.

---

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

Governing Phase B documents:

- `docs/data/PROVIDER_REGISTRY.md`
- `docs/data/SOURCE_COVERAGE_MATRIX.md`
- `docs/data/PIT_AVAILABILITY_MATRIX.md`
- `docs/data/IDENTITY_RULES.md`
- `docs/data/RULESET_ERAS.md`

---

## B.2 — Empirical Coverage & PIT Probe — ACTIVE

### B.2 public measurement pass — COMPLETE

Current evidence is recorded in:

- `docs/data/PROVIDER_PROBE_RESULTS_V1.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V2.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V1.md`

Research-only tooling:

- `scripts/probes/provider_coverage_probe.py`
- `tests/probes/test_provider_coverage_probe.py`

### Public empirical anchors now measured

#### 2024 completed-season cfbfastR build

The public build log reports:

```text
966 schedules
966 betting rows
162,953 PBP rows from 966 games
151,607 play-participant rows from 966 games
230,344 game-roster rows from 966 games
27,477 season athlete-team roster rows
0 injury rows from 966 games
```

This verifies a major availability conclusion:

```text
NO INJURY ROW != HEALTHY
```

The ESPN-derived public injury block cannot be treated as national college-football availability truth.

#### 2026 preseason cfbfastR build

The current public build reports:

```text
946 schedules
946 betting rows
1,776 power-index rows
0 PBP rows
0 game-roster rows
0 injury rows
```

The same log explicitly says the season has not started for PBP-derived products.

Therefore coverage state must distinguish at least:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

A zero-row preseason PBP dataset and a zero-row completed-season injury dataset are not semantically equivalent.

#### Historical PBP release era

Current SportsDataverse public release metadata verifies season-specific PBP artifacts from **2004 through 2025**.

This establishes artifact existence, not yet guaranteed training-quality completeness.

The current release artifacts were created/rebuilt long after many of the historical games, so:

```text
current historical artifact != historical knowledge snapshot
```

remains locked.

### Leakage guardrail now executable

The probe harness carries an explicit hazard list for verified cfbfastR next-play fields including:

```text
lead_text
lead_start_team
lead_start_yardsToEndzone
lead_start_down
lead_start_distance
lead_scoringPlay
```

Provider tables may never be wholesale-approved as model features.

---

## B.2 next active work

### B.2-A — CFBD authenticated representative row probe — NEXT / CREDENTIAL-GATED

The committed harness reads:

```text
CFBD_API_KEY
```

from the environment only.

Initial probe targets:

```text
GET /games
GET /plays
```

across representative seasons/weeks.

Measure:

- game and play counts;
- unique and duplicate IDs;
- neutral-site representation;
- conference/classification missingness;
- PBP game coverage;
- `wallclock`, PPA and play-text missingness;
- era/schema behavior.

Absence of a local key is recorded as `SKIPPED_NO_CFBD_API_KEY`, not provider failure.

### B.2-B — CFBD college-native family expansion

After the first authenticated games/PBP probe:

- teams/conferences;
- rosters/players;
- recruiting;
- transfers;
- returning production;
- coaches;
- lines;
- ratings/rankings.

### B.2-C — Cross-provider identity/reconciliation cases

Measure selected:

```text
CFBD <-> ESPN/cfbfastR game matches
CFBD <-> ESPN/cfbfastR player matches
transfer continuity
venue/conference agreement
play matching where practical
```

### B.2-D — Prospective live timestamp/revision capture

Once 2026 games produce live events, capture repeated observations with:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

before assigning high-confidence live PIT semantics.

### B.2-E — Availability-source trial

Because the public ESPN-derived 2024 injury build produced zero observations, evaluate:

- official conference/program availability feeds;
- SportsDataIO trial;
- Sportradar trial;

against explicit questions about timestamped pre-kickoff status, historical revisions, identity resolution, latency and missing-report behavior.

---

## Locked provider direction

### Adopt / integrate as primary candidates

- **CollegeFootballData (CFBD):** P0 college-native historical foundation and live candidate, pending B.2 authenticated measurements.
- **SportsDataverse / cfbfastR:** P0/P1 independent PBP/roster/participant reconstruction and research corpus.
- **NCAA official sources:** rules/stat/result reference and reconciliation.
- **College Football Playoff official sources:** postseason-format/competition truth.
- **Official conference/program availability reports:** required availability evidence family.
- **Daily-Data-Core:** shared owner of odds, weather, venue/geospatial, travel/rest, generic provenance, run lifecycle and settlement.

### Trial before adoption

- **SportsDataIO NCAA Football:** priority injury/availability trial.
- **Sportradar NCAA Football:** live/event/roster/change-log redundancy trial.

---

## Major gaps explicitly preserved

1. uniform national historical injury/availability timeline;
2. uniform historical published depth charts;
3. complete OC/DC/play-caller history;
4. complete redshirt/eligibility history;
5. exact timestamped historical sportsbook quote tape in the sport repo — belongs in `Daily-Data-Core`;
6. exact original publication/revision timing for several rich historical datasets;
7. authenticated CFBD row-level era measurements;
8. cross-provider player/game reconciliation rates.

These are architecture inputs, not reasons to fake completeness.

---

## Explicitly not started yet

- production canonical database schema;
- production provider ingestion code;
- broad historical backfill;
- production feature engineering;
- model training;
- simulation;
- Recommendation Gate implementation.

Small probe scripts/data remain research-only and must not silently become production acquisition.

---

## Phase B -> Phase C transition rule

Phase B closes only when:

1. the major F-0 through F-14 source families have empirically measured coverage where access permits;
2. inaccessible/commercial families are explicitly credential/trial-gated rather than guessed;
3. major PIT/revision semantics have validated classifications or conservative exclusion rules;
4. representative identity cases demonstrate acceptable game/program/player reconciliation;
5. the remaining gaps are precise enough that Phase C can design provider-independent canonical contracts;
6. no production schema decision depends on assuming a provider field is complete or PIT-safe without evidence.

Only then may Daily NCAAF advance to **Phase C — Canonical Schema & Identity Foundation**.
