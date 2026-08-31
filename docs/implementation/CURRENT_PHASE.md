# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. B.2-A CFBD games/PBP measurement complete. **B.2-B CFBD college-native coverage, era, scope, and identity audit is complete. B.2-C CFBD <-> ESPN/cfbfastR cross-provider reconciliation is now active.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

---

## Phase B — Source & Coverage Audit

### B.1 — Public Source & Contract Audit — COMPLETE

Completed artifacts include provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras, and Daily-Data-Core ownership boundaries.

---

## B.2 — Empirical Coverage, PIT & Reconciliation — ACTIVE

### B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings include:

- sampled game IDs and play IDs were unique;
- play text was effectively complete in measured strata;
- sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
- provider `wallclock` is not historical publication time and never replaces Daily-NCAAF `acquired_at`;
- PPA nullness is play-family dependent;
- `classification=fbs` returns an FBS-involved universe including FBS-vs-FCS games;
- the lone incomplete 2024 row was the real Liberty-at-App-State Hurricane Helene cancellation;
- 2026 responses changed between acquisitions, proving the need for immutable live observations.

Remaining event-side revision/PIT timing belongs to B.2-D.

---

## B.2-B — CFBD college-native family / identity audit — COMPLETE

Evidence now covers:

```text
teams / conference affiliations
rosters / recruiting
transfer portal / returning production
coaches
talent composite
rankings
Elo / SRS / SP+ / FPI / CORE
historical lines
player continuity
transfer continuity
coach continuity
missing recruit linkage
name collisions
```

### Provider-family boundaries

- CFBD team/player/coach IDs are strong provider crosswalk evidence, never canonical Daily-NCAAF IDs.
- direct recruiting `athleteId` linkage is materially incomplete;
- returning production is provider-derived and PIT-unresolved;
- ranking rows cannot be keyed only by `(season, week)`;
- historical CFBD lines are not timestamped sportsbook quote tape;
- sportsbook aliases, quote chronology, no-vig, and closing-snapshot policy remain owned by `Daily-Data-Core`;
- HTTP 429 is a transport/rate state, not missing data or exhausted monthly quota.

### Transfer portal coverage

Observed annual rows:

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

Portal observations expose useful transfer state but measured rows did not expose an explicit player/athlete identifier.

Therefore:

```text
portal row != standalone player identity
```

### Rating-family boundaries

- CORE public retrospective history begins in 2016 and is PIT-C by default.
- Elo year-only behavior is latest-available-week rather than an explicit canonical weekly snapshot.
- FPI closely tracks an FBS-sized universe in completed seasons but retains its own PIT/provenance contract.
- SP+ repeatedly has a near-FBS-plus-extra pattern.
- SRS expands well beyond FBS beginning in observed 2022 responses.

### Team Talent Composite exact membership

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

### Positive player identity continuity

Stable CFBD roster athlete IDs were observed for:

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

### Coach identity continuity

Stable provider coach IDs were observed across school changes:

```text
Nick Saban    406   Toledo -> Michigan State -> LSU -> Alabama
Kalen DeBoer  564   Fresno State -> Washington -> Alabama
Curt Cignetti 1741  James Madison -> Indiana
```

Canonical architecture remains:

```text
PERSON -> COACH -> COACH_ROLE_STINT
```

Coordinator/play-caller history remains a separate source gap.

### Missing recruit-linkage hard cases

Final B.2-B evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V10.md
```

Local test suite:

```text
Ran 9 tests in 0.003s
OK
```

Recruiting missingness measured:

| Year | Recruit rows | athleteId null | FBS-committed + athleteId null |
|---:|---:|---:|---:|
| 2021 | 3,364 | 1,115 | 437 |
| 2022 | 3,955 | 1,232 | 240 |
| 2023 | 4,166 | 1,503 | 240 |
| 2024 | 4,236 | 1,580 | 291 |

Across 12 selected FBS-committed missing-`athleteId` cases:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK                 0
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE     8
UNRESOLVED                                    4
```

No sampled roster `recruitIds` list directly contained the tested recruiting-record ID.

Locked consequence:

```text
roster.recruitIds cannot be assumed to directly join to the selected /recruiting/players record ID
```

without independent semantic proof.

### Name collision evidence

Normalized-name collisions occurred in every tested year.

Examples included:

```text
Andrew Jones
Austin Smith
AJ Barton
DJ Moore / D.J. Moore
Daniel Harris
Ashton Hampton
```

The 2022 AJ Barton example contained two recruiting records with the same normalized name, same committed program (UTEP), same position (OT), and null athlete IDs.

Therefore:

```text
NAME MATCH != IDENTITY MATCH
name + school != guaranteed unique identity
name + school + position != guaranteed unique identity
```

### Commitment semantics

Some sampled FBS recruiting commitments had no matching roster candidate in the bounded committed-program window.

Therefore:

```text
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
```

Commitment is recruiting-state evidence, not enrollment truth.

### Reconciliation states — LOCKED

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

Candidate evidence, competing candidates, provenance, confidence/version, and rejection reason must remain auditable.

No source row is forced onto a canonical player.

### Provider semantic caution

The CFBD roster payload field named `year` did not behave as the requested roster season in selected cases. Requested/query season must therefore be preserved explicitly as observation context.

Provider objects must not silently define canonical temporal/entity semantics.

---

# B.2-C — CFBD <-> ESPN/cfbfastR cross-provider reconciliation — ACTIVE

Governing plan:

```text
docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md
```

Initial harness/test:

```text
scripts/probes/cross_provider_game_reconciliation_probe.py
tests/probes/test_cross_provider_game_reconciliation_probe.py
```

### C1 — Game/event reconciliation — ACTIVE FIRST

Initial seasons:

```text
2024
2026
```

The public SportsDataverse `espn_cfb_schedules` dataset defines `game_id` as the ESPN event identifier. C1 therefore tests exact ID equality empirically rather than assuming it.

Measure:

1. CFBD game-ID uniqueness;
2. ESPN/cfbfastR game-ID uniqueness;
3. exact game-ID overlap;
4. CFBD -> ESPN exact-ID coverage;
5. raw ESPN-only event set without misclassifying universe differences as missing data;
6. matched home/away team names;
7. week agreement;
8. kickoff agreement;
9. score/lifecycle agreement where available;
10. season-specific source asset SHA-256 and acquisition time.

Critical rule:

```text
provider season totals are not comparable until event universe is normalized
```

If ESPN division/classification columns are present, the harness additionally computes an FBS-involved ESPN subset. Otherwise ESPN extras remain explicitly `UNIVERSE_UNNORMALIZED`.

### C2-C6 — queued after C1

```text
C2 program/team crosswalks
C3 player cross-provider identity
C4 transfer continuity
C5 venue/conference/context agreement
C6 selected play-level reconciliation
```

B.2-C successful matching does not make a historical source PIT-safe; PIT classification remains separate.

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

## Phase B -> Phase C production-schema transition rule

Production canonical schema is unlocked only when:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative cross-provider identity cases demonstrate acceptable game/program/player reconciliation;
5. remaining gaps are precise enough for provider-independent canonical contracts;
6. no schema depends on assuming a provider field is complete, unique, canonical, or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation, and Recommendation Gate implementation remain blocked until this gate is met.
