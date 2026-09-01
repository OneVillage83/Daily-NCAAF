# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity is COMPLETE/FROZEN and C2 program/team provider-crosswalk stability is ACTIVE.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

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

Final evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V14.md
```

The user-executed V4 suite passed all 10 tests.

### Completed 2024 freeze evidence

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
exact shared event IDs                    920
normalized ESPN FBS-involved events      920
normalized exact overlap                  920
normalized CFBD-only                        0
normalized ESPN-only                        0

SAME_SIDE                                 918
SWAPPED_SIDES                               2
UNRESOLVED                                  0
AMBIGUOUS                                   0

ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR  2

week MATCH                                920
score MATCH                               919
score UNAVAILABLE                           1
score MISMATCH                              0
lifecycle MATCH                           920

participant observations                 1840
unique CFBD team names                    230
unique ESPN team IDs                      230
CFBD-name -> multiple ESPN-ID conflicts     0
ESPN-ID -> multiple CFBD-name conflicts     0
matched games skipped                       0
```

The single unavailable score is the real Liberty-at-App-State cancellation.

### Frozen C1 identity rules

```text
provider home/away side != canonical participant identity
same exact event + same participant set + swapped provider sides != identity conflict
scores are compared only after participant alignment
provider season totals are compared only after event-universe normalization
```

Inside an exact-ID matched two-participant event:

```text
one strong participant alignment
+ no competing opposite-orientation anchor
=> remaining participant may be aligned by counterpart elimination
```

This resolved the two `Saint Francis` vs `St. Francis (PA) Red Flash` events without creating a global alias rule.

### Kickoff semantics remain separate

2024 V4 kickoff deltas:

```text
<= 60 seconds             905
> 60 sec <= 5 min           1
> 5 min <= 30 min            6
> 30 min <= 2 hours          6
> 2 hours                     2
```

These remain provider-time semantic observations, not C1 identity failures.

### 2026 remains acquisition-state evidence

At V4 acquisition:

```text
CFBD season events                    888
SportsDataverse/ESPN events             8
exact shared event IDs                  8
ESPN-only                                0
```

Three shared events were final in CFBD while the immutable SportsDataverse asset still carried `STATUS_IN_PROGRESS` and intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

This supports B.2-D but does not replace prospective repeated live capture.

---

## C2 — Program / team provider crosswalk — ACTIVE

Plan:

```text
docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_team_crosswalk_probe.py
tests/probes/test_cross_provider_team_crosswalk_probe.py
```

Initial completed-season window:

```text
2023
2024
2025
```

C2 uses the frozen C1 participant-aligned schedule crosswalk and independently fetches CFBD `/teams/fbs?year=`. It measures:

```text
FBS schedule-crosswalk coverage
CFBD team id == derived ESPN team id
within-season ID collisions
same school name -> multiple provider IDs across seasons
same provider ID -> multiple school names across seasons
FBS membership entry/exit transitions
```

Provider IDs remain crosswalks, never canonical `PROGRAM_ID` values.

C2 freeze requires complete or explicitly explained completed-season coverage, no unresolved within-season collisions, and direct provider-ID disagreements to be individually explained rather than normalized away.

---

## C3-C6 — queued after C2

```text
C3 player cross-provider identity
C4 transfer continuity across providers
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
