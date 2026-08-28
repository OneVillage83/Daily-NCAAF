# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT probe is active. The public SportsDataverse/cfbfastR measurement pass and the first authenticated CFBD games/PBP row-level pass are complete. A narrow B.2-A follow-up is active before B.2-B college-native family expansion. Phase C remains intentionally blocked pending sufficient provider-family and cross-provider evidence.

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

Current evidence:

- `docs/data/PROVIDER_PROBE_RESULTS_V1.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V2.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V3.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V1.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V2.md`

Research-only tooling:

- `scripts/probes/provider_coverage_probe.py`
- `tests/probes/test_provider_coverage_probe.py`

### Public empirical anchors

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

Locked consequence:

```text
NO INJURY ROW != HEALTHY
```

The ESPN-derived public injury block cannot be treated as national college-football availability truth.

#### 2026 preseason cfbfastR build

The public build reports schedules/betting before event products exist. Therefore coverage state must distinguish at least:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

A zero-row preseason PBP dataset and a zero-row completed-season injury dataset are not semantically equivalent.

#### Historical public PBP era

Current SportsDataverse release metadata verifies season-specific PBP artifacts from 2004 through 2025. Artifact existence is not historical PIT proof.

---

## B.2-A — CFBD authenticated representative row probe

### Initial authenticated pass — COMPLETE

A local run of the committed V1 harness successfully queried:

```text
GET /games
GET /plays
```

for seasons:

```text
2004, 2010, 2014, 2020, 2024, 2025, 2026
```

and representative weeks:

```text
1, 8, 15
```

Every request returned HTTP 200.

### Key measured findings

#### Game identity

- zero duplicate game-ID rows in every sampled season response;
- 2024 returned 920 rows / 920 unique IDs, with 919 marked complete;
- 2025 returned 934 / 934, all complete;
- 2026 returned 888 scheduled rows and zero completed rows at probe time;
- 2004 contained four conference-null observations; later sampled seasons contained none.

#### Play identity and text

Across the sampled played seasons:

- zero duplicate play-ID rows were observed;
- play text was effectively complete, with only one null row in the sampled 2024 set.

#### `wallclock` era break

Aggregated sampled-week null rates:

```text
2004  100.00%
2010  100.00%
2014  100.00%
2020    0.10%
2024    2.32%
2025    0.97%
```

Locked consequence:

```text
CFBD wallclock is optional by era
CFBD wallclock is not a universal historical publication timestamp
```

Daily-NCAAF live/PIT evidence must preserve its own `acquired_at` and immutable observation history.

#### PPA nullness

Aggregate PPA null rates across sampled played eras were roughly 22%-29%. Because these totals include administrative and special-teams play types where PPA may be structurally inapplicable, raw PPA nullness is not a generic PBP-completeness metric.

The V2 probe now measures PPA nullness by play type.

#### Cross-provider season universe mismatch

Earlier cfbfastR public build counts:

```text
2024 schedules = 966
2026 schedules = 946
```

CFBD authenticated `classification=fbs` counts:

```text
2024 games = 920
2026 games = 888
```

These differences are not labeled provider defects. Event universes must first be normalized for classification, cancellation/postponement, postseason and other inclusion semantics.

Locked consequence:

```text
NEVER compare provider season totals without normalizing event universe
```

---

## B.2-A focused follow-up — ACTIVE / NEXT LOCAL RUN

The probe harness is now versioned as:

```text
DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V2
```

It adds:

- game classification-pair counts;
- classification null counts;
- season-type counts;
- incomplete-game examples;
- score-missing/start-time-TBD counts;
- explicit query-scope metadata;
- normalized null rates;
- PPA and wallclock nullness by play type.

The next narrow run targets:

```text
2015, 2016, 2017, 2018, 2019, 2024, 2026
```

Goals:

1. locate the `wallclock` transition between 2014 and 2020;
2. identify the one incomplete 2024 row;
3. measure FBS/FCS classification-pair composition behind the CFBD season universe;
4. avoid carrying ambiguous provider-scope assumptions into B.2-C/Phase C.

---

## B.2-B — CFBD college-native family expansion — QUEUED NEXT

After the focused B.2-A follow-up:

- teams/conferences;
- rosters/players;
- recruiting;
- transfers;
- returning production;
- coaches;
- lines;
- ratings/rankings.

These will be probed family-by-family rather than by indiscriminate API download.

---

## B.2-C — Cross-provider identity/reconciliation cases

Measure selected:

```text
CFBD <-> ESPN/cfbfastR game matches
CFBD <-> ESPN/cfbfastR player matches
transfer continuity
venue/conference agreement
play matching where practical
```

The newly observed 2024/2026 season-universe deltas are explicit B.2-C targets rather than assumed completeness failures.

---

## B.2-D — Prospective live timestamp/revision capture

Once 2026 games produce live events, capture repeated observations with:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

before assigning high-confidence live PIT semantics.

---

## B.2-E — Availability-source trial

Because the public ESPN-derived 2024 injury build produced zero observations, evaluate:

- official conference/program availability feeds;
- SportsDataIO trial;
- Sportradar trial;

against explicit questions about timestamped pre-kickoff status, historical revisions, identity resolution, latency and missing-report behavior.

---

## Locked provider direction

### Adopt / integrate as primary candidates

- **CollegeFootballData (CFBD):** P0 college-native historical foundation and live candidate. Initial games/PBP empirical access is now verified; broader family/PIT evidence remains in Phase B.
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
7. exact CFBD `wallclock` transition boundary and modern missingness semantics;
8. normalized cross-provider game-universe reconciliation;
9. cross-provider player/game reconciliation rates;
10. broader authenticated CFBD roster/recruiting/transfer/coaching family measurements.

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
