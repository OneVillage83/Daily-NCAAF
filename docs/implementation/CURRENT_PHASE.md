# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity and C2 program/team provider crosswalk are COMPLETE/FROZEN; C3-A targeted player identity is COMPLETE and C3-B breadth/coverage reconciliation is ACTIVE.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

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

Detailed evidence is retained through `docs/data/PROVIDER_PROBE_RESULTS_V10.md`.

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

Stable CFBD player IDs survived same-program seasons, multiple transfers and FCS→FBS movement in selected cases. Stable coach IDs survived program changes. Recruiting linkage remains incomplete and name-only repair is unsafe.

---

# B.2-C — CFBD <-> ESPN/cfbfastR reconciliation — ACTIVE

## C1 — Game / event reconciliation — COMPLETE / FROZEN

Freeze contract:

```text
docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md
```

Completed 2024:

```text
exact shared event IDs                    920
normalized exact overlap                  920 / 920
normalized CFBD-only                        0
normalized ESPN-only                        0
SAME_SIDE                                 918
SWAPPED_SIDES                               2
UNRESOLVED                                  0
AMBIGUOUS                                   0
score MATCH                               919
score UNAVAILABLE                           1
score MISMATCH                              0
week MATCH                                920
team-ID crosswalk conflicts                 0
```

Provider home/away side is not canonical identity. Kickoff discrepancies remain temporal-semantics evidence, not identity failures.

---

## C2 — Program / team provider crosswalk — COMPLETE / FROZEN

Freeze contract:

```text
docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md
```

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V15.md
```

Completed 2023-2025:

```text
2023  133 / 133 FBS programs mapped; 133 direct CFBD-ID == ESPN-ID matches
2024  134 / 134 FBS programs mapped; 134 direct CFBD-ID == ESPN-ID matches
2025  136 / 136 FBS programs mapped; 136 direct CFBD-ID == ESPN-ID matches
```

Cross-season:

```text
unique FBS school names                        136
unique CFBD team IDs                           136
unique ESPN team IDs                           136
same school -> multiple provider IDs             0
same ESPN ID -> multiple CFBD school names       0
same CFBD ID -> multiple CFBD school names       0
```

The audited sources expose the same numeric external team-ID namespace over this window, while canonical Daily-NCAAF `PROGRAM_ID` remains independent.

Measured FBS membership entries:

```text
2024: Kennesaw State
2025: Delaware, Missouri State
```

---

## C3 — Player cross-provider identity — ACTIVE

### C3-A targeted identity — COMPLETE

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V16.md
```

Tooling:

```text
scripts/probes/cross_provider_player_identity_probe.py
tests/probes/test_cross_provider_player_identity_probe.py
```

User-executed suite:

```text
11 tests
OK
```

Target continuity:

```text
Jalen Milroe 4432734
  2023 Alabama     DIRECT_SHARED_PROVIDER_ID
  2024 Alabama     DIRECT_SHARED_PROVIDER_ID

Dillon Gabriel 4427238
  2022 Oklahoma    DIRECT_SHARED_PROVIDER_ID
  2023 Oklahoma    DIRECT_SHARED_PROVIDER_ID
  2024 Oregon      DIRECT_SHARED_PROVIDER_ID

Caleb Downs 4870706
  2023 Alabama     DIRECT_SHARED_PROVIDER_ID
  2024 Ohio State  DIRECT_SHARED_PROVIDER_ID
  2025 Ohio State  DIRECT_SHARED_PROVIDER_ID

Travis Hunter 4685415
  2022 Jackson State  CFBD_ONLY_IDENTIFIER
  2023 Colorado       DIRECT_SHARED_PROVIDER_ID
  2024 Colorado       DIRECT_SHARED_PROVIDER_ID
```

Hunter's 2022 state is a source coverage gap, not an identity conflict: SportsDataverse exposed zero Jackson State roster rows while CFBD exposed 119.

Locked:

```text
ZERO PROVIDER TEAM ROWS != PLAYER ABSENCE
provider-only roster row != identity disagreement
```

Across the nine measured FBS team-season slices:

```text
CFBD unique athlete IDs                  1111
ESPN unique athlete IDs                  1111
exact shared athlete IDs                 1099
CFBD-only athlete IDs                      12
ESPN-only athlete IDs                      12
weighted exact-ID overlap               98.92% / 98.92%
duplicate athlete-ID slices                 0
```

This is strong evidence that recent FBS CFBD roster IDs and ESPN-derived `athlete_id` values share the same external athlete-ID namespace. It is not a roster-completeness claim.

Display-name variants occurred on the same exact athlete ID, further locking:

```text
name inequality != identity break
```

### C3-B breadth / coverage — ACTIVE

Plan:

```text
docs/data/B2C_C3_PLAYER_COVERAGE_BREADTH_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_player_coverage_probe.py
tests/probes/test_cross_provider_player_coverage_probe.py
```

The deterministic 13-slice breadth sample spans:

```text
2024: Clemson, Michigan, Utah, Georgia, Army, Kennesaw State,
      Toledo, Boise State, App State, Oregon State, Notre Dame
2025: Delaware, Missouri State
```

This covers major-conference, Group-of-Five, independent, service-academy, conference-realignment and recent-FBS-entry contexts.

C3 may freeze after C3-B only if the broader sample continues to show a dominant shared athlete-ID namespace without unexplained collisions, while provider-only rows and zero-team coverage remain explicit source-coverage states.

---

## C4-C6 — queued after C3

```text
C4 transfer-event / broader continuity reconciliation
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

The 2026 source-state lag observed during C1 supports this gate but does not replace prospective repeated capture.

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
