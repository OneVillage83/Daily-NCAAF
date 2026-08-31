# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT probe remains active. B.2-A core authenticated CFBD games/PBP representative measurement is now complete; B.2-B college-native family expansion is active. Phase C remains intentionally blocked pending broader family and cross-provider evidence.

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
- `docs/data/PROVIDER_PROBE_RESULTS_V4.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V1.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V2.md`
- `docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md`

Research-only tooling:

- `scripts/probes/provider_coverage_probe.py`
- `tests/probes/test_provider_coverage_probe.py`
- `scripts/probes/cfbd_native_family_probe.py`
- `tests/probes/test_cfbd_native_family_probe.py`

---

## Public empirical anchors

### 2024 completed-season cfbfastR build

The public build log reported extensive schedule/PBP/participant/roster coverage while producing zero injury rows.

Locked consequence:

```text
NO INJURY ROW != HEALTHY
```

The ESPN-derived public injury block cannot be treated as national college-football availability truth.

### Historical public PBP era

Current SportsDataverse release metadata verifies season-specific PBP artifacts from 2004 through 2025. Artifact existence is not historical PIT proof.

### Coverage state

Dataset readiness must distinguish at least:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

A structural preseason zero and a completed-season source gap are not semantically equivalent.

---

## B.2-A — CFBD games/PBP representative audit — CORE COMPLETE

### Initial authenticated pass

The local authenticated V1 probe successfully queried representative `/games` and `/plays` strata across:

```text
2004, 2010, 2014, 2020, 2024, 2025, 2026
```

with weeks:

```text
1, 8, 15
```

Every request returned HTTP 200.

### Focused V2 follow-up

The second authenticated pass queried:

```text
2015, 2016, 2017, 2018, 2019, 2024, 2026
```

with the same representative weeks and additional classification/status/null diagnostics. The local V2 helper test suite reported:

```text
Ran 8 tests
OK
```

### Locked findings

#### Game/play identifiers

Across the sampled strata:

- no duplicate game IDs were observed in season responses;
- no duplicate play IDs were observed in sampled weeks;
- play text was effectively complete in measured modern/historical samples.

This supports CFBD as a strong historical event/PBP candidate while still requiring cross-provider reconciliation and full-season validation.

#### `wallclock` era boundary

Observed sampled behavior:

```text
2014 -> 100% null
2015 -> 100% null
2016 -> 100% null
2017 -> 100% null
2018 -> generally populated with small gaps
2019+ -> generally populated with small gaps
```

The current empirical coverage-era candidate is:

```text
PRE_2018  -> wallclock unavailable in tested strata
2018_PLUS -> wallclock generally available but nullable
```

Locked consequences:

```text
CFBD wallclock is optional by era
CFBD wallclock is not a universal historical publication timestamp
Daily-NCAAF acquired_at remains mandatory for observed live/PIT evidence
```

#### PPA semantics

The V2 follow-up demonstrated that overall PPA nullness is dominated by play-family semantics. Rush/pass scrimmage plays are typically near-complete while many kickoff/punt/penalty/timeout/end-period rows are structurally null.

Locked consequence:

```text
PPA IS NULL != invalid play
```

PPA eligibility must be defined by normalized play family before feature use.

#### CFBD FBS query universe

Observed `classification=fbs` responses include FBS-vs-FCS games. Representative season composition included:

```text
2024: 799 FBS-vs-FBS + 121 FBS-vs-FCS = 920 rows
2026: 761 FBS-vs-FBS + 127 FBS-vs-FCS = 888 rows
```

Locked consequence:

```text
NEVER compare provider season totals without normalizing event universe
```

The earlier CFBD↔cfbfastR row-count delta remains a B.2-C reconciliation problem, not an assumed provider defect.

#### 2024 incomplete game resolved

The one incomplete 2024 row is:

```text
Liberty at App State
2024-09-28
CFBD game id 401640992
```

Official school records identify this as the Hurricane Helene cancellation that was not rescheduled.

Locked consequence:

```text
scheduled != played
historical incomplete row != automatically missing final
```

Phase C must preserve event lifecycle/status semantics.

#### 2026 live-state evolution observed

The later authenticated snapshot now contained eight completed 2026 games and 1,412 week-1 PBP rows across eight games while future weeks remained empty.

This reinforces the need for B.2-D repeated acquisition with immutable raw evidence and `acquired_at`; one current snapshot cannot reconstruct when rows first appeared or later changed.

### B.2-A status

The representative **core games/PBP audit is complete enough to advance**. Remaining event-side questions move to later subphases:

- full-season completeness;
- CFBD↔cfbfastR game/play reconciliation;
- player-play association completeness;
- prospective live publication/revision timing.

---

## B.2-B — CFBD college-native family expansion — ACTIVE

Specification:

```text
docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md
```

Harness:

```text
scripts/probes/cfbd_native_family_probe.py
```

Initial families:

```text
teams / historical conference affiliation
rosters
recruiting
transfer portal
returning production
coaches
talent composite
rankings
ratings
historical lines
```

### Initial measurements

#### Teams / conference affiliations

Measure provider team IDs, duplicates, conference/classification behavior and historical affiliation representation. This feeds the canonical:

```text
SCHOOL -> PROGRAM -> PROGRAM_SEASON -> CONFERENCE_AFFILIATION_STINT
```

architecture.

#### Rosters / recruiting linkage

Measure roster player-ID uniqueness and missingness plus `recruitIds` linkage. Recruiting records expose nullable `athleteId`, allowing us to measure recruit-to-college-player linkage instead of guessing.

No name-only auto-merges are permitted.

#### Transfer portal

Measure transfer destination/date/rating/stars/eligibility behavior by era.

A transfer remains a new `PLAYER_PROGRAM_STINT`, not a new player identity.

#### Returning production

Measure family coverage by era but preserve it as a derived provider feature until PIT/reconstruction semantics are established.

#### Coaches

Measure historical head-coach IDs and nested season behavior. This family does not solve coordinator/play-caller history by itself.

#### Rankings / ratings

Measure historical coverage family-by-family. Poll snapshots, Elo, SRS, SP+, FPI and CORE must retain distinct provenance/PIT semantics.

CFBD documents historical CORE output as retrospective methodology output; it is not automatically a historical PIT feature.

#### Historical lines

Measure game/provider/field availability without changing the ownership boundary:

```text
historical line response != timestamped sportsbook quote tape
```

Daily-Data-Core remains responsible for sportsbook quote snapshots, no-vig and market chronology.

### B.2-B next local run

After pulling the branch and with `CFBD_API_KEY` still set locally:

```powershell
python -m unittest discover -s tests/probes -p "test_cfbd_native_family_probe.py" -v

python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2014,2018,2024,2026 `
  --teams "Alabama,Michigan,Notre Dame,Boise State" `
  --output local-data/probes/cfbd_native_families_v1.json
```

If API tier/quota constraints appear, rerun using smaller `--families` subsets rather than interpreting the error as missing data.

---

## B.2-C — Cross-provider identity/reconciliation — QUEUED

Measure selected:

```text
CFBD <-> ESPN/cfbfastR game matches
CFBD <-> ESPN/cfbfastR player matches
transfer continuity
venue/conference agreement
play matching where practical
```

The 2024/2026 season-universe deltas and provider classification semantics are explicit targets.

---

## B.2-D — Prospective live timestamp/revision capture — ACTIVE WHEN GAMES ARE LIVE

Repeatedly capture selected 2026 games with:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

before assigning high-confidence live PIT semantics.

---

## B.2-E — Availability-source trial — QUEUED

Because the public ESPN-derived 2024 injury build produced zero observations, evaluate:

- official conference/program availability feeds;
- SportsDataIO trial;
- Sportradar trial;

against explicit timestamp, revision, identity, latency and missing-report questions.

---

## Locked provider direction

### Primary candidates

- **CollegeFootballData (CFBD):** P0 college-native historical foundation and live candidate; B.2-A event/PBP representative access verified, B.2-B broader native-family audit active.
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
7. normalized cross-provider game-universe reconciliation;
8. cross-provider player/game reconciliation rates;
9. broader authenticated CFBD roster/recruiting/transfer/coaching family measurements;
10. historical roster/recruiting/transfer revision semantics;
11. prospective live update/correction timing.

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
