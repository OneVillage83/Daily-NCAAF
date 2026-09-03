# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity, C2 program/team provider crosswalk and C3 player cross-provider identity are COMPLETE/FROZEN; C4 transfer-event reconciliation is ACTIVE.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

---

# Phase B — Source, Coverage, PIT & Reconciliation Audit

## B.1 — Public Source & Contract Audit — COMPLETE

Provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras and Daily-Data-Core ownership boundaries are documented.

## B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings include:

- sampled game IDs and play IDs were unique;
- sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
- provider `wallclock` is not publication time and never replaces Daily-NCAAF `acquired_at`;
- PPA nullness is play-family dependent;
- `classification=fbs` is an FBS-involved universe including FBS-vs-FCS games;
- Liberty-at-App-State 2024 is a real cancellation;
- current-season responses change across acquisitions, requiring immutable observations.

Prospective correction/revision timing remains B.2-D.

---

## B.2-B — CFBD college-native family / identity audit — COMPLETE

Locked:

```text
provider team/player/coach ID != canonical Daily-NCAAF identity
transfer != new player identity
classification change != new player identity
NAME MATCH != IDENTITY MATCH
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
NO TALENT ROW != ZERO TALENT
HTTP 429 != missing data
```

Stable CFBD player IDs survived same-program seasons, multiple transfers and FCS->FBS movement in selected cases. Recruiting linkage remains incomplete and name-only repair is unsafe.

---

# B.2-C — CFBD <-> ESPN/cfbfastR reconciliation — ACTIVE

## C1 — Game / event reconciliation — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md
```

Completed 2024 established 920/920 normalized FBS event overlap, zero unresolved/ambiguous orientations, zero score mismatches and zero team-ID crosswalk conflicts.

Provider home/away side is not canonical identity. Kickoff differences remain temporal-semantics evidence, not identity failures.

---

## C2 — Program / team provider crosswalk — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md
```

Completed 2023-2025:

```text
2023  133 / 133 direct CFBD-ID == ESPN-ID
2024  134 / 134 direct CFBD-ID == ESPN-ID
2025  136 / 136 direct CFBD-ID == ESPN-ID
```

No measured cross-season ID collision occurred. External provider team ID remains separate from canonical `PROGRAM_ID`.

---

## C3 — Player cross-provider identity — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md
```

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V16.md
docs/data/PROVIDER_PROBE_RESULTS_V17.md
```

### C3-A targeted continuity

```text
Jalen Milroe 4432734
  Alabama 2023/2024: direct shared provider ID

Dillon Gabriel 4427238
  Oklahoma 2022/2023 -> Oregon 2024: direct shared provider ID throughout

Caleb Downs 4870706
  Alabama 2023 -> Ohio State 2024/2025: direct shared provider ID throughout

Travis Hunter 4685415
  Jackson State 2022: CFBD-only under zero ESPN team-row coverage
  Colorado 2023/2024: direct shared provider ID
```

### C3-A nine FBS slices

```text
CFBD athlete-ID observations       1111
ESPN athlete-ID observations       1111
shared                             1099
weighted overlap                 98.92% / 98.92%
duplicate-ID slices                  0
```

### C3-B deterministic 13-slice breadth pass

User-executed suite:

```text
10 tests
OK
```

Aggregate:

```text
CFBD athlete-ID observations       1634
ESPN athlete-ID observations       1638
shared                             1616
CFBD-only                            18
ESPN-only                            22
weighted CFBD overlap            98.8984%
weighted ESPN overlap            98.6569%
minimum CFBD slice overlap       94.1606%
minimum ESPN slice overlap       88.6179%
zero-team-row slices                 0
duplicate-ID slices                  0
```

Coverage states:

```text
COMPLETE_EXACT_ID_SET_MATCH  4
HIGH_EXACT_ID_OVERLAP        7
PARTIAL_EXACT_ID_OVERLAP     2
```

Across C3-A + C3-B's 22 FBS slices:

```text
CFBD athlete-ID observations       2745
ESPN athlete-ID observations       2749
shared                             2715
combined weighted CFBD overlap   98.9071%
combined weighted ESPN overlap   98.7632%
```

These are observation counts across slices, not globally unique persons.

Frozen:

```text
shared external athlete ID = strong provider-crosswalk identity evidence
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
name inequality != identity break
shared cross-provider ID != historical PIT safety
```

---

## C4 — Transfer-event reconciliation — ACTIVE

Plan:

```text
docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_transfer_event_probe.py
tests/probes/test_cross_provider_transfer_event_probe.py
```

Initial transfer events:

```text
Dillon Gabriel  UCF 2021 -> Oklahoma 2022
Dillon Gabriel  Oklahoma 2023 -> Oregon 2024
Travis Hunter   Jackson State 2022 -> Colorado 2023
Caleb Downs     Alabama 2023 -> Ohio State 2024
```

C4 treats CFBD portal rows as contextual transfer observations because the measured portal schema does not expose a direct athlete ID. Frozen C3 athlete IDs bracket the surrounding pre/post roster stints.

Required distinction:

```text
portal row != player identity
transferDate != publication time
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
```

---

## C5-C6 — queued after C4

```text
C5 venue/conference/context agreement
C6 selected play-level reconciliation
```

Cross-provider matching never makes a historical source PIT-safe by itself.

---

## B.2-D — Prospective live timestamp/revision capture — STILL REQUIRED

Required repeated evidence:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

The 2026 source-state lag observed during C1 supports this gate but does not replace prospective repeated live capture.

## B.2-E — Availability-source trial — QUEUED

Evaluate official conference/program feeds plus commercial trials against timestamp, revision, identity, latency and missing-report criteria because the public ESPN-derived injury family produced zero observations across completed 2024.

---

# Phase B -> Phase C transition rule

Production canonical schema remains blocked until:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative cross-provider game/program/player reconciliation supports provider-independent identity contracts;
5. remaining gaps are explicit rather than assumed away;
6. no schema assumes a provider field is complete, unique, canonical or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
