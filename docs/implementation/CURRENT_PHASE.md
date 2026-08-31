# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT work remains active. B.2-A core authenticated CFBD games/PBP measurement is complete. B.2-B broad college-native family discovery and the continuous 2015–2026 portal/talent/rating era scan are now complete; targeted entity-scope and identity cases are active. Phase C remains intentionally blocked.

---

## Phase B — Source & Coverage Audit

### B.1 — Public Source & Contract Audit — COMPLETE

Completed artifacts include:

- provider registry;
- source coverage matrix;
- PIT availability matrix;
- canonical identity rules;
- ruleset eras;
- Daily-Data-Core ownership boundaries.

---

## B.2 — Empirical Coverage & PIT Probe — ACTIVE

Current evidence includes:

- `docs/data/PROVIDER_PROBE_RESULTS_V1.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V2.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V3.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V4.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V5.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V6.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V7.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V1.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V2.md`
- `docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md`
- `docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md`
- `docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V2.md`
- `docs/data/CFBD_NATIVE_IDENTITY_SCOPE_PLAN_V1.md`

Research-only tooling:

- `scripts/probes/provider_coverage_probe.py`
- `tests/probes/test_provider_coverage_probe.py`
- `scripts/probes/cfbd_native_family_probe.py`
- `tests/probes/test_cfbd_native_family_probe.py`
- `scripts/probes/cfbd_talent_scope_probe.py`
- `tests/probes/test_cfbd_talent_scope_probe.py`

---

## Public empirical anchors — LOCKED

### SportsDataverse / cfbfastR

The completed 2024 public build demonstrated extensive schedule/PBP/participant/roster coverage while producing zero injury rows.

```text
NO INJURY ROW != HEALTHY
```

Historical PBP artifacts currently span 2004–2025, but current artifact publication timestamps are not historical information-availability timestamps.

Coverage states must distinguish:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

---

## B.2-A — CFBD games/PBP representative audit — CORE COMPLETE

Locked findings:

1. no duplicate game IDs were observed in sampled season responses;
2. no duplicate play IDs were observed in sampled weeks;
3. play text was effectively complete in measured strata;
4. sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
5. `wallclock` is not a historical publication timestamp and never replaces Daily-NCAAF `acquired_at`;
6. PPA nullness is play-family dependent;
7. `classification=fbs` returns an FBS-involved universe including FBS-vs-FCS games;
8. the lone incomplete 2024 row was Liberty at App State, a real Hurricane Helene cancellation;
9. 2026 provider responses changed between snapshots, proving the need for immutable current-season observations.

Remaining event-side questions move to B.2-C/B.2-D:

- full-season cross-provider completeness;
- CFBD ↔ cfbfastR game/play reconciliation;
- player-play association completeness;
- prospective live revision/publication timing.

---

## B.2-B — CFBD college-native family expansion

### Broad family pass — COMPLETE

Representative seasons:

```text
2014
2018
2024
2026
```

Representative roster programs:

```text
Alabama
Michigan
Notre Dame
Boise State
```

Families measured:

```text
teams
conference affiliations
rosters
recruiting
transfer portal
returning production
coaches
talent
rankings
Elo / SRS / SP+ / FPI / CORE
historical lines
```

The local native-family test suite reported:

```text
Ran 8 tests
OK
```

### Core provider-family findings — LOCKED

#### Teams / conference affiliations

CFBD FBS team IDs were unique/non-null in representative seasons and affiliation rows aligned strongly with the season-specific FBS program set.

Provider IDs remain crosswalks, not canonical Daily-NCAAF identities.

Historical conference state is useful for PIT-B reconstruction but is not proof of original publication timing.

#### Rosters / recruiting

Roster athlete IDs were clean in the sampled programs, but direct recruiting linkage is incomplete.

Observed recruiting `athleteId` direct-link rates:

```text
2014 -> 47.4%
2018 -> 47.4%
2024 -> 62.7%
2026 -> 55.7%
```

Required reconciliation states:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

No name-only auto-merge is permitted.

#### Returning production

Coverage is broad, but this remains a provider-derived feature family whose historical PIT semantics are unresolved.

#### Coaches

Year-filtered coach IDs were unique in representative queries, but multi-season/team continuity still requires targeted case studies. Coordinator/play-caller history remains a separate source gap.

#### Rankings

Historical poll data is rich, but some seasons return multiple rows labeled week `1`; ranking snapshots cannot be keyed only by `(season, week)`.

#### Historical lines

CFBD historical line data has useful market evidence but variable field richness by era and no timestamped quote chronology.

Observed provider alias drift includes:

```text
DraftKings
Draft Kings
```

Therefore sportsbook identity/aliasing, quote `acquired_at`, no-vig and market chronology remain owned by `Daily-Data-Core`.

```text
CFBD historical lines != timestamped sportsbook quote tape
```

---

## Continuous portal/talent/rating era scan — COMPLETE

The annual 2015–2026 scan plus clean 2025 retry resolves the broad-era questions sufficiently to stop indiscriminate endpoint harvesting.

### Transfer portal

Observed annual row counts:

```text
2015      0
2016      0
2017      0
2018      0
2019      0
2020      0
2021   1770
2022   2273
2023   2502
2024   3378
2025   4499
2026   4470  (prior representative snapshot)
```

Locked provider coverage boundary:

```text
PRE_2021 -> no portal rows in tested annual queries
2021_PLUS -> substantial portal coverage
```

This is an API/source boundary, not a historical publication timestamp.

2025 portal missingness:

```text
destination null 729 / 4499  ~= 16.2%
rating null      1988 / 4499 ~= 44.2%
stars null        686 / 4499 ~= 15.2%
transferDate null   0 / 4499 =   0.0%
```

Missing destination/rating remains valid uncertainty/state information, not automatically bad data.

### Talent composite

Observed unique-team counts:

```text
2015 232
2016 237
2017 157
2018 236
2019 231
2020 219
2021 224
2022 233
2023 238
2024 134
2025 134
2026 138  (prior representative snapshot)
```

This disproves any universal assumption that `/talent` is FBS-only historically.

The 2025 response also prevents locking a simple `2024+ == FBS membership` rule: 2025 talent returned 134 teams while FBS-sized rating families returned 136.

Therefore row-count inference ends here. Exact team-set membership comparison is now required.

### Rating-family boundaries

#### CORE

Public retrospective rows begin in 2016.

```text
CORE historical public output = PIT-C by default
```

#### Elo

Year-only queries represent latest-available-week behavior, not a canonical explicit weekly snapshot.

#### FPI

Completed-season counts closely track the FBS-sized universe and make FPI a strong external benchmark/source candidate, while PIT provenance remains separate.

#### SP+

Repeatedly returns approximately the FBS-sized universe plus one extra/null-conference row; entity reconciliation is required.

#### SRS

Observed counts include:

```text
2021 130
2022 261
2023 261
2024 265 rows / 263 unique teams
2025 266 rows / 265 unique teams
```

SRS therefore cannot be treated as FBS-only or normalized by row count.

### Transport/rate semantics

The long era scan triggered temporary HTTP 429 responses. Provider output explicitly identified these as short-period rate limiting rather than exhausted monthly quota.

Locked rule:

```text
HTTP 429 != missing dataset
HTTP 429 != empty coverage
HTTP 429 != monthly quota exhausted
```

Targeted follow-up tooling should pace requests and use bounded retry/backoff.

---

## B.2-B targeted scope & identity cases — ACTIVE / NEXT

Governing plan:

```text
docs/data/CFBD_NATIVE_IDENTITY_SCOPE_PLAN_V1.md
```

### Target 1 — talent membership scope

Use:

```text
scripts/probes/cfbd_talent_scope_probe.py
```

for:

```text
2023
2024
2025
2026
```

Compare exact provider membership from:

```text
/teams/fbs?year=<season>
/talent?year=<season>
```

Measure exact overlap plus missing/extra team sets. Do not fuzzy-normalize away provider-name mismatches.

### Target 2 — player identity cases

Required bounded cases:

- same-program multi-season player;
- single transfer;
- multiple transfers;
- recruit with direct `athleteId`;
- recruit without direct `athleteId` but later roster evidence;
- FBS/FCS mover;
- similar-name collision;
- jersey/position change.

### Target 3 — coach continuity

Measure provider coach-ID continuity across seasons and team changes, including an interim transition where possible.

---

## B.2-C — Cross-provider identity/reconciliation — QUEUED

Required evidence:

```text
CFBD <-> ESPN/cfbfastR game matches
CFBD <-> ESPN/cfbfastR player matches
transfer continuity
venue/conference agreement
play matching where practical
```

The targeted B.2-B identity cases should feed directly into B.2-C.

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

Because the public ESPN-derived injury family produced zero observations across a completed 2024 build, evaluate:

- official conference/program availability feeds;
- SportsDataIO trial;
- Sportradar trial;

against timestamp, revision, identity, latency and missing-report criteria.

---

## Phase B -> Phase C transition rule

Phase B closes only when:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative identity cases demonstrate acceptable program/game/player reconciliation;
5. remaining gaps are precise enough for provider-independent canonical contracts;
6. no production schema depends on assuming a provider field is complete or PIT-safe without evidence.

Production canonical schema, broad backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
