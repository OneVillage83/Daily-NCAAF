# B.2-C C3-B — Player Cross-Provider Breadth / Coverage Plan V1

Status: **COMPLETE**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3-A targeted player identity — COMPLETE

## Objective

Determine whether the high exact athlete-ID overlap measured in C3-A generalizes beyond the four targeted continuity programs, without turning provider roster coverage into an identity assumption.

C3-B is a deterministic breadth pass, not a full historical backfill.

## Deterministic sample

```text
2024: Clemson, Michigan, Utah, Georgia, Army, Kennesaw State,
      Toledo, Boise State, App State, Oregon State, Notre Dame
2025: Delaware, Missouri State
```

The sample spans major-conference, Group-of-Five, independent, service-academy, recent-FBS-entry and conference-realignment contexts.

## User-executed result

```text
10 tests
OK
```

Probe aggregate:

```text
sample slices                              13
compared non-empty slices                  13
complete exact-ID set match slices          4
high exact-ID overlap slices                7
partial exact-ID overlap slices             2
zero CFBD team-row slices                   0
zero ESPN team-row slices                   0
duplicate-ID slices                         0

CFBD unique athlete IDs                  1634
ESPN unique athlete IDs                  1638
exact shared athlete IDs                 1616
CFBD-only athlete IDs                      18
ESPN-only athlete IDs                      22
weighted CFBD overlap                  98.8984%
weighted ESPN overlap                  98.6569%
minimum CFBD slice overlap             94.1606%
minimum ESPN slice overlap             88.6179%
```

Detailed evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V17.md
```

## Coverage interpretation

Four slices were exact set matches:

```text
App State 2024
Oregon State 2024
Delaware 2025
Missouri State 2025
```

The lowest measured CFBD-side overlap was Georgia 2024 at `94.1606%`. The lowest ESPN-side overlap was Utah 2024 at `88.6179%` because ESPN exposed 14 athlete IDs not present in the CFBD slice.

Neither case contained duplicate athlete IDs or a contradictory same-ID mapping.

Locked:

```text
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
```

## C3-A + C3-B combined FBS evidence

```text
team-season slices                        22
CFBD athlete-ID observations            2745
ESPN athlete-ID observations            2749
exact shared athlete-ID observations   2715
combined weighted CFBD overlap       98.9071%
combined weighted ESPN overlap       98.7632%
```

These are observation counts across slices, not globally unique-person counts.

## Safety rules

```text
provider athlete ID != canonical PLAYER_ID
name equality != identity proof
name inequality != identity break
classification/program membership != player identity
shared provider ID != PIT safety
```

## Exit

All C3-B freeze-candidate criteria were satisfied:

1. the broader FBS sample retained a dominant exact shared athlete-ID namespace;
2. no unexplained provider-ID collision appeared;
3. provider-only rows remain explicit source coverage differences;
4. zero-team coverage remains an explicit state where present in other strata;
5. C3-A transfer continuity remains valid direct identifier evidence;
6. canonical `PLAYER_ID` remains independent from provider IDs.

C3-B is complete and C3 is frozen by `B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md`.
