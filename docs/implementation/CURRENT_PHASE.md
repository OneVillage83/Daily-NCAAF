# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT probe remains active. B.2-A core authenticated CFBD games/PBP representative measurement is complete. B.2-B's first broad college-native family pass is also complete; a focused era/scope follow-up is active before B.2-C identity/reconciliation. Phase C remains intentionally blocked.

---

## Active phase

### Phase B — Source & Coverage Audit

#### B.1 — Public Source & Contract Audit — COMPLETE

Completed artifacts include provider registry, source coverage matrix, PIT availability matrix, identity rules, ruleset eras and Daily-Data-Core ownership boundaries.

---

## B.2 — Empirical Coverage & PIT Probe — ACTIVE

Current evidence:

- `docs/data/PROVIDER_PROBE_RESULTS_V1.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V2.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V3.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V4.md`
- `docs/data/PROVIDER_PROBE_RESULTS_V5.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V1.md`
- `docs/data/PROVIDER_COVERAGE_PROBE_SPEC_V2.md`
- `docs/data/CFBD_NATIVE_FAMILY_PROBE_SPEC_V1.md`
- `docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md`

Research-only tooling:

- `scripts/probes/provider_coverage_probe.py`
- `tests/probes/test_provider_coverage_probe.py`
- `scripts/probes/cfbd_native_family_probe.py`
- `tests/probes/test_cfbd_native_family_probe.py`

---

## Public empirical anchors — LOCKED

### SportsDataverse/cfbfastR

The completed 2024 public build demonstrated extensive schedule/PBP/participant/roster coverage but zero injury rows.

```text
NO INJURY ROW != HEALTHY
```

Historical public PBP artifacts currently span 2004-2025, but modern artifact publication timestamps are not historical information-availability timestamps.

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

The authenticated V1/V2 passes established enough event-side evidence to advance.

Locked findings:

1. no duplicate game IDs were observed in sampled season responses;
2. no duplicate play IDs were observed in sampled weeks;
3. play text was effectively complete in the measured strata;
4. sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
5. `wallclock` is not a historical publication timestamp and never replaces Daily-NCAAF `acquired_at`;
6. PPA nullness is strongly play-family dependent;
7. `classification=fbs` returns an FBS-involved universe including FBS-vs-FCS games;
8. the one incomplete 2024 game was Liberty at App State, a real Hurricane Helene cancellation;
9. 2026 responses evolved between probe snapshots, proving the need for immutable current-season observations.

Remaining event-side questions now belong to B.2-C/B.2-D:

- full-season cross-provider completeness;
- CFBD↔cfbfastR game/play reconciliation;
- player-play association completeness;
- prospective live revision/publication timing.

---

## B.2-B — CFBD college-native family expansion

### Initial broad pass — COMPLETE

Local tests:

```text
Ran 8 tests in 0.001s
OK
```

Authenticated representative seasons:

```text
2014
2018
2024
2026
```

Roster programs:

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

Every family call in this pass returned HTTP 200.

### B.2-B locked findings

#### Teams

FBS team IDs were unique and non-null in all representative seasons:

```text
2014 -> 128 / 128 unique
2018 -> 130 / 130 unique
2024 -> 134 / 134 unique
2026 -> 138 / 138 unique
```

Current role:

```text
PRIMARY PROVIDER CROSSWALK CANDIDATE
```

Provider IDs remain crosswalks, not canonical internal IDs.

#### Historical conference affiliations

The affiliation family matched the tested FBS team counts with no null team IDs or conferences. Historical `endYear` state is clearly retrospective/current provider truth and therefore useful for PIT-B reconstruction, not proof of historical publication timing.

Canonical architecture remains:

```text
SCHOOL -> PROGRAM -> PROGRAM_SEASON -> CONFERENCE_AFFILIATION_STINT
```

#### Rosters and recruit linkage

Roster player IDs were unique/non-null in all sampled teams. Direct roster `recruitIds` linkage was incomplete and materially variable by era/program:

```text
sampled range ~= 33% to 86%
```

Modern physical/position fields were highly complete; older 2014 weight coverage was materially weaker.

Locked rule:

```text
empty recruitIds -> unresolved linkage
empty recruitIds != no recruiting record
```

#### Recruiting

Recruit IDs were unique/non-null, but direct `athleteId` linkage rates were:

```text
2014 -> 47.4%
2018 -> 47.4%
2024 -> 62.7%
2026 -> 55.7%
```

This proves that recruit→college-player identity cannot depend only on provider direct linkage.

Required reconciliation states include at least:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

No name-only auto-merge is permitted.

#### Transfer portal

Observed rows:

```text
2014 -> 0
2018 -> 0
2024 -> 3,378
2026 -> 4,470
```

2024/2026 transfer dates were complete, but destinations and ratings were often missing. Missing destination is valid transfer-state information, not automatically bad data.

Historical availability floor remains unresolved and is the first focused follow-up target.

#### Returning production

Rows were broad and returned PPA/usage fields were complete in the tested samples:

```text
2014 -> 125 teams
2018 -> 130
2024 -> 133
2026 -> 136
```

This remains a derived provider feature family. It is useful for research/baselines but is not automatically historical PIT input.

#### Coaches

Year-filtered coach IDs were unique and every returned row contained the queried year. However the first pass does not prove multi-season person/coach ID continuity or coordinator/play-caller history.

#### Talent composite

Observed rows:

```text
2014 -> 0
2018 -> 236
2024 -> 134
2026 -> 138
```

The 2018 response is much broader than the measured 130-team FBS universe and cannot be normalized by assumption. Talent scope/era is explicitly unresolved.

#### Ratings

Observed counts:

```text
          Elo   SRS   SP+   FPI   CORE
2014      130   128   129   128      0
2018      131   130   131   130    130
2024      134   265   135   134    134
2026       16     0   139   138      0
```

Locked consequences:

- rating families do not share one entity universe or readiness state;
- CORE historical output is retrospective/PIT-C unless prospectively captured;
- Elo year-only queries do not define an explicit week snapshot;
- SRS can return a broader universe than FBS and needs overlap/division measurement;
- SP+/FPI remain external model outputs requiring their own PIT/provenance contracts.

#### Rankings

Historical responses were rich; 2026 currently has only one early-season snapshot. Some historical responses contained more than one snapshot row labeled week `1`, so ranking identity cannot be keyed only by `(season, week)`.

#### Historical lines

Week-1 coverage:

```text
2014 -> 81 / 84 games
2018 -> 84 / 88
2024 -> 110 / 125
2026 -> 144 / 144
```

Field richness changes substantially by era. Older responses have spread evidence but no opening fields or moneylines; modern responses contain partial opening/moneyline fields.

The 2026 provider-name set contains both:

```text
DraftKings
Draft Kings
```

which empirically locks sportsbook alias normalization into `Daily-Data-Core`.

```text
CFBD historical lines != timestamped sportsbook quote tape
```

Daily-Data-Core remains authoritative for sportsbook identity, quote `acquired_at`, price chronology, no-vig and closing-snapshot policy.

---

## B.2-B focused follow-up — ACTIVE / NEXT

Plan:

```text
docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md
```

### Follow-up A — portal/talent/rating era scan

Use the existing B.2-B harness over:

```text
2015-2026
families = portal,talent,ratings
```

Goals:

1. locate the first non-zero transfer-portal season;
2. locate talent availability/scope transitions;
3. map annual CORE/Elo/SRS/SP+/FPI readiness;
4. identify years where rating/talent universes materially exceed FBS scope;
5. separate current-season structural zeros from historical unavailability.

### Follow-up B — identity cases

After era boundaries are located, measure representative actual identities:

- same-program multi-season player;
- transfer player;
- multiple-transfer player;
- direct recruit `athleteId` link;
- recruit without direct `athleteId` but later roster presence;
- similar-name collision;
- position/jersey change;
- coach continuity across seasons/teams.

This work will feed B.2-C rather than creating premature canonical tables.

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

Because the public ESPN-derived injury family produced zero observations across a completed 2024 build, evaluate official conference/program feeds plus SportsDataIO/Sportradar trials against explicit timestamp, revision, identity, latency and missing-report criteria.

---

## Phase B -> Phase C transition rule

Phase B closes only when:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative identity cases demonstrate acceptable program/game/player reconciliation;
5. remaining gaps are precise enough for provider-independent canonical contracts;
6. no production schema depends on assuming a provider field is complete or PIT-safe without evidence.

Production canonical schema, broad backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until that gate is met.
