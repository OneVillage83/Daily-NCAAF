# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. B.2-A CFBD games/PBP measurement complete. **B.2-B CFBD college-native family/era/scope/identity audit is complete. B.2-C cross-provider reconciliation is active, with C1 game identity at its final participant-alignment gate.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

---

# Phase B — Source, Coverage, PIT & Reconciliation Audit

## B.1 — Public Source & Contract Audit — COMPLETE

Completed artifacts include provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras, and Daily-Data-Core ownership boundaries.

---

## B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings:

- sampled game IDs and play IDs were unique;
- play text was effectively complete in measured strata;
- sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
- provider `wallclock` is not historical publication time and never replaces Daily-NCAAF `acquired_at`;
- PPA nullness is play-family dependent;
- `classification=fbs` is an FBS-involved event universe including FBS-vs-FCS games;
- the lone incomplete 2024 row was the real Liberty-at-App-State Hurricane Helene cancellation;
- 2026 responses changed between acquisitions, proving the need for immutable current-state observations.

Remaining prospective correction/revision timing belongs to B.2-D.

---

## B.2-B — CFBD college-native family / identity audit — COMPLETE

Detailed evidence is retained in `PROVIDER_PROBE_RESULTS_V1` through `V10`.

### Locked provider-family boundaries

- provider team/player/coach IDs are strong crosswalk evidence, never canonical Daily-NCAAF IDs;
- direct recruiting `athleteId` linkage is materially incomplete;
- returning production is provider-derived and PIT-unresolved;
- ranking rows cannot be keyed only by `(season, week)`;
- historical CFBD lines are not timestamped sportsbook quote tape;
- sportsbook aliases, quote chronology, no-vig and closing-snapshot policy remain owned by `Daily-Data-Core`;
- HTTP 429 is a transport/rate state, not missing data.

### Transfer portal

Observed annual portal rows were zero from 2015-2020 and substantial from 2021 onward. The measured portal records exposed useful transfer context but no explicit player identifier.

```text
portal row != standalone player identity
```

### Rating families

- CORE public retrospective history begins in 2016 and is PIT-C by default;
- Elo year-only queries are latest-available-week, not explicit canonical weekly snapshots;
- FPI, SP+, SRS, Elo and CORE retain separate entity-universe and temporal contracts.

### Team Talent Composite

Exact membership audit:

| Season | FBS | Talent | Missing FBS | Outside FBS | Exact match |
|---:|---:|---:|---:|---:|:---:|
| 2023 | 133 | 238 | 0 | 105 | No |
| 2024 | 134 | 134 | 0 | 0 | Yes |
| 2025 | 136 | 134 | 2 | 0 | No |
| 2026 | 138 | 138 | 0 | 0 | Yes |

2025 is missing exactly Air Force and Navy.

```text
NO TALENT ROW != ZERO TALENT
NO TALENT ROW != NON-FBS
```

### Player continuity

Stable CFBD roster athlete IDs survived:

```text
Jalen Milroe    Alabama 2021-2024
Dillon Gabriel UCF -> Oklahoma -> Oregon
Travis Hunter  Jackson State FCS -> Colorado FBS
Caleb Downs    Alabama -> Ohio State
```

Locked:

```text
transfer != new player identity
classification change != new player identity
provider athlete ID != canonical Daily-NCAAF identity
```

### Coach continuity

Stable provider coach IDs were measured across program changes for Nick Saban, Kalen DeBoer and Curt Cignetti.

Canonical architecture remains:

```text
PERSON -> COACH -> COACH_ROLE_STINT
```

### Missing recruit linkage / collisions

Across 12 sampled FBS-committed recruiting rows with `athleteId = null`:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK                 0
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE     8
UNRESOLVED                                    4
```

No sampled roster `recruitIds` list directly contained the tested recruiting-row ID.

Normalized-name collisions occurred in every tested year, including a 2022 case with two UTEP OT recruiting records sharing the same normalized name and null athlete IDs.

Locked:

```text
NAME MATCH != IDENTITY MATCH
name + school != guaranteed unique identity
name + school + position != guaranteed unique identity
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
```

Reconciliation states remain:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

No source row is forced onto a canonical identity.

---

# B.2-C — CFBD <-> ESPN/cfbfastR reconciliation — ACTIVE

Governing plan:

```text
docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md
```

## C1 — Game/event reconciliation — FINAL CORRECTION GATE

### C1 V1

V1 established the first 2024 exact-ID result but had two harness defects:

- ESPN mascot-bearing display names were incorrectly treated as team mismatches;
- V1 fabricated a `cfb_schedule_2026.csv.gz` path when the public release exposed 2026 as plain CSV/parquet/RDS.

Those were tooling errors, not provider failures.

### C1 V2 measured result

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V12.md
```

2024:

```text
CFBD FBS-involved events             920
SportsDataverse/ESPN events          966
exact shared game IDs                920
CFBD-only raw IDs                       0
ESPN-only raw IDs                      46
```

After deriving the ESPN FBS-involved universe from exact matched participants:

```text
ESPN FBS-involved event IDs          920
exact overlap with CFBD              920
CFBD-only after normalization           0
ESPN-only after normalization           0
```

This is strong evidence that the measured CFBD game ID and SportsDataverse/ESPN `game_id` share the ESPN event-ID namespace for the complete 2024 FBS-involved universe.

### Provider side orientation is not identity

V2 produced two apparent score mismatches and four apparent team-ID crosswalk conflicts. They came from exactly two bowl events:

```text
401677085  UTSA / Coastal Carolina
401677093  USC / Texas A&M
```

The providers contained the same event and same two teams but assigned opposite `home` / `away` sides.

Therefore:

```text
same event + same participant set + swapped provider sides != identity conflict
home/away label != canonical participant identity
```

Scores and team-ID crosswalks must be compared after participant alignment.

### 2024 temporal fields

Before participant-side correction:

```text
week agreement            920 / 920
kickoff <= 60 seconds     905 / 920
kickoff > 60 seconds       15 / 920
lifecycle agreement       920 / 920
raw side score mismatch     2 / 920  <- side-swap artifact
score unavailable           1 / 920
```

The 15 kickoff differences range from minutes to many hours. They are temporal-semantics evidence, not automatic provider errors.

```text
provider kickoff disagreement != bad record
```

Canonical architecture must preserve provider time observations with provenance and distinguish scheduled/revised/actual-start semantics where evidence supports those meanings.

### 2026 snapshot evidence

At the V2 acquisition:

```text
CFBD season events                        888
SportsDataverse schedule events             8
exact shared event IDs                      8
ESPN-only IDs                                0
```

All eight SportsDataverse events were exact CFBD game IDs and all eight kickoff timestamps agreed.

Three matched games showed current-state lag: CFBD already contained final scores and `completed=true` while the exact downloaded SportsDataverse asset still contained `STATUS_IN_PROGRESS` with intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
same event ID may carry different current state at the same audit time
```

This strengthens B.2-D's immutable observation requirement but does not replace prospective repeated capture.

### SportsDataverse release mutability

During this audit the public release manifest continued changing. Newer plain CSV assets appeared for historical seasons while older `.csv.gz` files remained present. The 2026 CSV retained the same 1,504-byte digest across later release-level updates.

Therefore:

```text
manifest-driven asset discovery is required
newest supported asset outranks stale format preference
source hash + acquired_at are mandatory
```

### C1 V3 — ACTIVE NEXT

Tooling:

```text
scripts/probes/cross_provider_game_reconciliation_probe_v3.py
tests/probes/test_cross_provider_game_reconciliation_probe_v3.py
```

Spec:

```text
docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V2.md
```

V3 performs:

1. exact game-ID matching;
2. participant orientation inside that matched event;
3. explicit `SAME_SIDE`, `SWAPPED_SIDES`, `AMBIGUOUS`, `UNRESOLVED` states;
4. score comparison after participant alignment;
5. team-ID crosswalk derivation after participant alignment;
6. FBS event-universe derivation after participant alignment;
7. snapshot-subset classification without turning current provider lag into historical missingness;
8. kickoff delta buckets and field-specific mismatch evidence;
9. newest-supported-asset selection with advertised-digest verification.

### C1 exit criterion

C1 may close when the corrected run demonstrates, for completed 2024:

- complete normalized event-ID overlap;
- no unexplained team-ID crosswalk conflicts;
- provider side swaps surfaced explicitly;
- scores aligned by participant identity;
- remaining kickoff differences retained as temporal-semantics observations rather than silently normalized.

Current 2026 remains snapshot/revision evidence only.

---

## C2-C6 — queued after C1

```text
C2 program/team provider crosswalk freeze
C3 player cross-provider identity
C4 transfer continuity across providers
C5 venue/conference/context agreement
C6 selected play-level reconciliation
```

Cross-provider matching never makes a historical source PIT-safe by itself.

---

## B.2-D — Prospective live timestamp/revision capture — ACTIVE WHEN GAMES ARE LIVE

Required repeated observations:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

The V2 2026 SportsDataverse-vs-CFBD lifecycle lag is supporting evidence for this gate, not a substitute for repeated capture.

---

## B.2-E — Availability-source trial — QUEUED

Because the public ESPN-derived injury family produced zero observations across a completed 2024 build, evaluate official conference/program feeds plus commercial trials against timestamp, revision, identity, latency and missing-report criteria.

---

# Phase B -> Phase C production-schema transition rule

Production canonical schema remains blocked until:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative cross-provider identity cases demonstrate acceptable game/program/player reconciliation;
5. remaining gaps are precise enough for provider-independent canonical contracts;
6. no schema depends on assuming a provider field is complete, unique, canonical or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
