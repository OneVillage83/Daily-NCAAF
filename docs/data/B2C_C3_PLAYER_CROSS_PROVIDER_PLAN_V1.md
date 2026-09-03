# B.2-C C3 — Player Cross-Provider Identity Plan V1

Status: **COMPLETE / FROZEN**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN

## Objective

Determine whether CFBD roster athlete identifiers and ESPN-derived SportsDataverse roster athlete identifiers provide strong direct cross-provider player identity evidence, including across transfers, without using names as identity keys.

## C3-A targeted identity — COMPLETE

Targets:

```text
Jalen Milroe     4432734
Dillon Gabriel   4427238
Travis Hunter    4685415
Caleb Downs      4870706
```

User-executed suite:

```text
11 tests
OK
```

Direct shared-ID continuity was observed for Milroe's measured Alabama seasons, Gabriel's Oklahoma->Oregon path, Downs' Alabama->Ohio State path and Hunter's Colorado seasons.

Hunter's 2022 Jackson State stint remained CFBD-only because the ESPN-derived roster asset exposed zero Jackson State rows. That is source coverage missingness, not an athlete-ID disagreement.

Across nine FBS roster slices:

```text
CFBD athlete-ID observations       1111
ESPN athlete-ID observations       1111
shared                             1099
CFBD-only                            12
ESPN-only                            12
weighted overlap                 98.92% / 98.92%
duplicate-ID slices                  0
```

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V16.md
```

## C3-B breadth / coverage — COMPLETE

User-executed suite:

```text
10 tests
OK
```

The deterministic 13-slice sample covered conference, independent, service-academy, realignment and recent-FBS-entry contexts.

Aggregate:

```text
CFBD athlete-ID observations       1634
ESPN athlete-ID observations       1638
shared                             1616
CFBD-only                            18
ESPN-only                            22
weighted CFBD overlap            98.8984%
weighted ESPN overlap            98.6569%
zero-team-row slices                 0
duplicate-ID slices                  0
```

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V17.md
docs/data/B2C_C3_PLAYER_COVERAGE_BREADTH_PLAN_V1.md
```

## Combined measured FBS evidence

```text
team-season slices                        22
CFBD athlete-ID observations            2745
ESPN athlete-ID observations            2749
exact shared athlete-ID observations   2715
combined weighted CFBD overlap       98.9071%
combined weighted ESPN overlap       98.7632%
```

These are observation counts across slices, not globally unique-person counts.

## Frozen rules

```text
provider athlete ID != canonical PLAYER_ID
shared external athlete ID = strong provider-crosswalk identity evidence
name equality != identity proof
name inequality != identity break
same player + transfer != new PLAYER
FCS -> FBS != new PLAYER
missing provider roster row != player absence
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
shared cross-provider ID != historical PIT safety
```

Names may discover or diagnose candidates, but they may never repair a provider-ID conflict.

## Production contract direction

```text
PLAYER
  canonical player_id

PLAYER_PROVIDER_CROSSWALK
  player_id
  provider
  provider_athlete_id
  reconciliation_method
  evidence/provenance
  observed_at / acquired_at
  confidence

PLAYER_PROGRAM_STINT
  canonical player_id
  canonical program_id
  stint interval / season state
  evidence/provenance
```

The provider athlete ID never becomes the canonical Daily-NCAAF `PLAYER_ID`.

## Freeze contract

```text
docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md
```

## Exit

C3 is complete/frozen. C4 is the next reconciliation gate and will evaluate identifier-less transfer portal observations against the frozen player/program identities and surrounding roster-stint evidence.
