# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. Phase B.1 public source/contract audit complete. B.2-A CFBD games/PBP measurement core complete. **B.2-B CFBD college-native family/era/scope/identity audit is complete. B.2-C cross-provider reconciliation is active, with C1 game/event identity at its final V4 counterpart-anchor exit gate.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

---

# Phase B — Source, Coverage, PIT & Reconciliation Audit

## B.1 — Public Source & Contract Audit — COMPLETE

Provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras, and Daily-Data-Core ownership boundaries are documented.

## B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings include:

- sampled game IDs and play IDs were unique;
- sampled `wallclock` is absent through 2017 and generally available-but-nullable from 2018 forward;
- provider `wallclock` is not publication time and never replaces Daily-NCAAF `acquired_at`;
- PPA nullness is play-family dependent;
- `classification=fbs` is an FBS-involved universe including FBS-vs-FCS games;
- Liberty-at-App-State 2024 is a real cancellation, not a missing completion artifact;
- current-season responses change across acquisitions, requiring immutable observations.

Prospective correction/revision timing remains B.2-D.

---

## B.2-B — CFBD college-native family / identity audit — COMPLETE

Detailed evidence is retained through `docs/data/PROVIDER_PROBE_RESULTS_V10.md`.

Locked identity/source rules include:

```text
provider team/player/coach ID != canonical Daily-NCAAF identity
transfer != new player identity
classification change != new player identity
NAME MATCH != IDENTITY MATCH
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
NO TALENT ROW != ZERO TALENT
HTTP 429 != missing data
```

Observed player continuity included Jalen Milroe, Dillon Gabriel, Travis Hunter and Caleb Downs. Stable coach IDs were measured across program changes for Nick Saban, Kalen DeBoer and Curt Cignetti. Recruiting `athleteId` linkage is materially incomplete, roster `recruitIds` did not directly recover the sampled missing-link recruiting rows, and normalized-name collisions occurred in every tested recruiting year.

---

# B.2-C — CFBD <-> ESPN/cfbfastR reconciliation — ACTIVE

## C1 — Game/event reconciliation — FINAL V4 EXIT GATE

Latest evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V13.md
docs/data/B2C_GAME_RECONCILIATION_FOLLOWUP_V3.md
```

### V3 completed measurement

The user-executed V3 run passed all 14 unit tests and produced:

```text
contract = DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V3
```

2024 event universe:

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
exact shared event IDs                    920
CFBD-only raw IDs                           0
ESPN-only raw IDs                          46
normalized ESPN FBS-involved events      920
normalized exact overlap                  920
normalized CFBD-only                        0
normalized ESPN-only                        0
```

This is strong empirical evidence that the measured CFBD game ID and SportsDataverse/ESPN `game_id` share the ESPN event-ID namespace for the complete 2024 FBS-involved universe.

### Provider home/away side is not identity

V3 correctly resolves two postseason side swaps:

```text
401677085  UTSA / Coastal Carolina
401677093  USC / Texas A&M
```

Both become score matches after participant alignment.

Locked:

```text
same event + same participant set + swapped provider sides != identity conflict
provider home/away side != canonical participant identity
```

### V3 remaining edge case

V3 participant orientation counts:

```text
SAME_SIDE       916
SWAPPED_SIDES     2
UNRESOLVED        2
```

The only unresolved exact-ID events are:

```text
401644732  Kent State vs Saint Francis
401644737  Eastern Michigan vs Saint Francis
```

CFBD uses `Saint Francis`; ESPN/SportsDataverse uses `St. Francis (PA) Red Flash`. In each event, the other participant is independently aligned on the same side.

The correct general reconciliation rule is therefore:

```text
EXACT EVENT ID
+ two-participant event
+ one strong participant alignment
+ no competing opposite-orientation anchor
=> remaining participant may be aligned by counterpart elimination
```

This is not a global hard-coded alias rule.

### V4 tooling — ACTIVE NEXT

```text
scripts/probes/cross_provider_game_reconciliation_probe_v4.py
tests/probes/test_cross_provider_game_reconciliation_probe_v4.py
```

V4 preserves V3's event-ID, side-swap, score-alignment, asset-freshness and snapshot semantics while adding explicit alignment-basis evidence:

```text
TWO_PARTICIPANT_DISPLAY_EVIDENCE
ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR
COMPETING_TWO_PARTICIPANT_DISPLAY_EVIDENCE
COMPETING_ONE_PARTICIPANT_ANCHORS
INSUFFICIENT_PARTICIPANT_DISPLAY_EVIDENCE
```

V4 must never use a one-participant anchor when the opposite orientation has competing strong evidence.

### C1 freeze requirements

For completed 2024, require:

```text
exact shared IDs                           920
normalized FBS overlap                     920 / 920
normalized CFBD-only                         0
normalized ESPN-only                         0
unresolved orientation                       0
ambiguous orientation                        0
team crosswalk conflicts                     0
score mismatch                               0
week mismatch                                0
```

Expected audit shape if the source artifact is unchanged:

```text
SAME_SIDE                                  918
SWAPPED_SIDES                                2
ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR 2
score MATCH                                919
score UNAVAILABLE                            1
participant observations                  1840
unique CFBD names                          230
unique ESPN IDs                            230
```

These are exit expectations, not hard-coded production truths.

### Kickoff semantics remain separate

2024 V3 kickoff deltas:

```text
<= 60 seconds             905
> 60 sec <= 5 min           1
> 5 min <= 30 min            6
> 30 min <= 2 hours          6
> 2 hours                     2
```

Provider kickoff disagreement remains source-time evidence until scheduled/revised/actual-start semantics are proven.

### 2026 acquisition-state evidence

At V3 acquisition:

```text
CFBD season events                    888
SportsDataverse/ESPN events             8
exact shared event IDs                  8
ESPN-only                                0
```

All eight shared kickoff timestamps matched. Three exact matched events were already final in CFBD while the immutable downloaded SportsDataverse asset still contained `STATUS_IN_PROGRESS` and intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

This supports B.2-D but does not replace prospective repeated live capture.

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

Required repeated evidence:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

## B.2-E — Availability-source trial — QUEUED

Evaluate official conference/program feeds plus commercial trials against timestamp, revision, identity, latency, and missing-report criteria because the public ESPN-derived injury family produced zero observations across completed 2024.

---

# Phase B -> Phase C transition rule

Production canonical schema remains blocked until:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative cross-provider game/program/player reconciliation is strong enough for provider-independent identity contracts;
5. remaining gaps are explicit rather than silently assumed away;
6. no schema assumes a provider field is complete, unique, canonical or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
