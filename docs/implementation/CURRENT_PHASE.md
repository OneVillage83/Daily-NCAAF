# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. Phase B.2 empirical coverage/PIT work remains active. B.2-A core CFBD games/PBP measurement is complete. B.2-B broad college-native coverage, annual era scanning, Team Talent Composite scope, and positive player/coach continuity cases are complete. The active B.2-B gate is now the missing-recruit-linkage/name-collision audit. Phase C remains intentionally blocked.

---

## Phase B — Source & Coverage Audit

### B.1 — Public Source & Contract Audit — COMPLETE

Completed artifacts include provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras, and Daily-Data-Core ownership boundaries.

---

## B.2 — Empirical Coverage & PIT Probe — ACTIVE

### Completed evidence blocks

#### B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings include:

- sampled game IDs and play IDs were unique;
- play text was effectively complete in measured strata;
- sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
- provider `wallclock` is not historical publication time and never replaces Daily-NCAAF `acquired_at`;
- PPA nullness is play-family dependent;
- `classification=fbs` includes FBS-vs-FCS games;
- the lone incomplete 2024 row was the real Liberty-at-App-State Hurricane Helene cancellation;
- 2026 responses changed between acquisitions, proving the need for immutable live observations.

#### B.2-B — broad college-native family discovery — COMPLETE

Measured families include:

```text
teams / conference affiliations
rosters / recruiting
transfer portal / returning production
coaches
talent composite
rankings
Elo / SRS / SP+ / FPI / CORE
historical lines
```

Key locked boundaries:

- CFBD team and coach/player IDs are provider crosswalk evidence, never canonical IDs;
- direct recruiting `athleteId` linkage is useful but incomplete;
- returning production is provider-derived and PIT-unresolved;
- rankings cannot be keyed only by `(season, week)`;
- historical lines are not timestamped sportsbook quote tape;
- sportsbook aliases/quote chronology/no-vig remain owned by `Daily-Data-Core`.

#### Continuous portal/talent/rating era scan — COMPLETE

Transfer-portal annual rows:

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
2026   4470  (prior current-state snapshot)
```

Locked source boundary:

```text
PRE_2021 -> no portal rows in tested annual queries
2021_PLUS -> substantial portal coverage
```

Current-season row counts remain snapshot observations, not final-season trend values.

Rating contracts remain family-specific:

- CORE public retrospective history begins in 2016 and is PIT-C by default;
- Elo year-only behavior is latest-available-week rather than an explicit weekly snapshot;
- FPI closely tracks the FBS-sized universe in completed seasons;
- SP+ repeatedly has a near-FBS-plus-extra pattern;
- SRS expands well beyond FBS beginning in observed 2022 responses.

HTTP 429 is a transport/rate state, not missing data or exhausted monthly quota.

#### Team Talent Composite exact membership — COMPLETE

| Season | FBS | Talent | Overlap | Missing FBS | Outside FBS | Exact match |
|---:|---:|---:|---:|---:|---:|:---:|
| 2023 | 133 | 238 | 133 | 0 | 105 | No |
| 2024 | 134 | 134 | 134 | 0 | 0 | Yes |
| 2025 | 136 | 134 | 134 | 2 | 0 | No |
| 2026 | 138 | 138 | 138 | 0 | 0 | Yes |

2025 is missing exactly:

```text
Air Force
Navy
```

Locked rules:

```text
NO TALENT ROW != ZERO TALENT
NO TALENT ROW != NON-FBS
```

Talent observations must be reconciled against canonical `PROGRAM_SEASON` membership with explicit coverage state.

---

## Positive player/transfer/coach identity continuity — COMPLETE

Evidence document:

```text
docs/data/PROVIDER_PROBE_RESULTS_V9.md
```

Harness/test:

```text
scripts/probes/cfbd_identity_case_probe.py
tests/probes/test_cfbd_identity_case_probe.py
```

The local suite reported:

```text
Ran 9 tests in 0.001s
OK
```

### Players

Measured roster athlete-ID continuity:

```text
Jalen Milroe   4432734  Alabama 2021-2024
Dillon Gabriel 4427238  UCF 2019-2021 -> Oklahoma 2022-2023 -> Oregon 2024
Travis Hunter  4685415  Jackson State FCS 2022 -> Colorado FBS 2023-2024
Caleb Downs    4870706  Alabama 2023 -> Ohio State 2024-2025
```

All four measured recruiting rows exposed `athleteId` values that directly matched the stable roster IDs.

Locked consequences:

```text
transfer != new player identity
classification change != new player identity
provider athlete ID = strong crosswalk evidence
provider athlete ID != canonical Daily-NCAAF identity
```

### Transfer portal

Measured portal rows for Gabriel, Hunter, and Downs exposed contextual fields but no explicit player/athlete identifier.

Therefore:

```text
portal row != standalone player identity
```

Portal data is modeled as a `TRANSFER_OBSERVATION` that must be reconciled to canonical player identity.

### Coaches

Measured stable provider coach IDs:

```text
Nick Saban    406   Toledo -> Michigan State -> LSU -> Alabama
Kalen DeBoer  564   Fresno State -> Washington -> Alabama
Curt Cignetti 1741  James Madison -> Indiana
```

Locked consequence:

```text
school change != new coach identity
```

Daily-NCAAF retains canonical:

```text
PERSON -> COACH -> COACH_ROLE_STINT
```

The coach endpoint does not solve historical OC/DC/play-caller coverage.

### Provider semantic caution discovered

The roster payload field named `year` did not behave as the requested roster season in the selected player cases. Requested/query season must therefore be stored explicitly as observation context; the provider field cannot silently define canonical season semantics.

The coach payload also mixes identity/role history with season results and derived ratings such as SP+/SRS. Those fields must be normalized separately rather than embedding the provider coach object wholesale.

---

## B.2-B missing recruit-linkage / name-collision audit — ACTIVE / NEXT

Specification:

```text
docs/data/CFBD_RECRUIT_LINKAGE_GAP_PROBE_SPEC_V1.md
```

Harness/test:

```text
scripts/probes/cfbd_recruit_linkage_gap_probe.py
tests/probes/test_cfbd_recruit_linkage_gap_probe.py
```

Target years:

```text
2021
2022
2023
2024
```

Research question:

```text
recruit.athleteId = null
-> can roster.recruitIds recover a direct provider link?
```

Allowed audit interpretations:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
AMBIGUOUS_NAME_COLLISION
UNRESOLVED
```

Only the first is explicit provider-link recovery. Name matching remains candidate discovery only.

The same probe also surfaces normalized-name collisions in recruiting data to demonstrate why names cannot be primary keys.

### B.2-B exit rule

B.2-B can close when this hard-case probe establishes the behavior of missing `athleteId` records and name ambiguity without exposing a new unresolved provider-identity failure mode.

Then advance to **B.2-C**.

---

## B.2-C — CFBD <-> ESPN/cfbfastR reconciliation — QUEUED

Required evidence:

```text
CFBD <-> cfbfastR game matches
CFBD <-> cfbfastR player matches
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

Because the public ESPN-derived injury family produced zero observations across a completed 2024 build, evaluate official conference/program feeds plus SportsDataIO/Sportradar trials against timestamp, revision, identity, latency, and missing-report criteria.

---

## Phase B -> Phase C transition rule

Phase B closes only when:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative identity cases demonstrate acceptable program/game/player reconciliation;
5. remaining gaps are precise enough for provider-independent canonical contracts;
6. no production schema depends on assuming a provider field is complete or PIT-safe without evidence.

Production canonical schema, broad backfill, feature engineering, training, simulation, and Recommendation Gate implementation remain intentionally blocked until this gate is met.
