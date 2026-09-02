# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity and C2 program/team provider crosswalk are COMPLETE/FROZEN; C3 player cross-provider identity is ACTIVE.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

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

Final completed-2024 evidence:

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
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

Provider home/away side is not canonical identity. Exact-event counterpart anchoring is permitted only when one participant is strongly aligned and the opposite orientation has no competing identity evidence.

Kickoff discrepancies remain temporal-semantics evidence, not identity failures.

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

The user-executed C2 suite passed all 11 tests.

### Completed-season evidence

```text
2023
FBS programs                         133
schedule-derived ESPN mappings      133
coverage                            100%
CFBD id == ESPN id                  133
mismatches                            0

2024
FBS programs                         134
schedule-derived ESPN mappings      134
coverage                            100%
CFBD id == ESPN id                  134
mismatches                            0

2025
FBS programs                         136
schedule-derived ESPN mappings      136
coverage                            100%
CFBD id == ESPN id                  136
mismatches                            0
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

The measured CFBD and ESPN-derived sources therefore expose the same numeric external team-ID namespace across the audited 2023-2025 FBS window.

Locked:

```text
external team ID != canonical PROGRAM_ID
provider display-name change != identity change
FBS membership transition != new PROGRAM identity
```

Measured FBS entries:

```text
2024: Kennesaw State
2025: Delaware, Missouri State
```

`App State` also demonstrated benign provider display-name evolution while external ID `2026` remained stable.

---

## C3 — Player cross-provider identity — ACTIVE

Plan:

```text
docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_player_identity_probe.py
tests/probes/test_cross_provider_player_identity_probe.py
```

### Initial targeted identities

```text
Jalen Milroe     4432734
Dillon Gabriel   4427238
Travis Hunter    4685415
Caleb Downs      4870706
```

The C3-A probe compares exact athlete identifiers in CFBD rosters against ESPN-derived SportsDataverse season rosters and also measures complete athlete-ID overlap for every surrounding team-season roster slice.

Targeted continuity includes:

```text
same-program continuity
FBS -> FBS transfers
FCS -> FBS movement
multi-season post-transfer continuity
```

Names are diagnostic candidate discovery only and never identity authority.

Required identity states remain explicit:

```text
DIRECT_SHARED_PROVIDER_ID
CFBD_ONLY_IDENTIFIER
ESPN_ONLY_IDENTIFIER
IDENTIFIER_DISAGREEMENT
AMBIGUOUS_NAME_CANDIDATES
UNRESOLVED
```

SportsDataverse roster assets are manifest-selected and immutable audit evidence records include source hash, advertised digest and acquired-at time.

---

## C4-C6 — queued after C3

```text
C4 transfer continuity / broader player reconciliation if C3-A requires expansion
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
