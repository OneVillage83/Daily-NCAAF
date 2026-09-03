# Provider Probe Results V17 — C3-B Player Cross-Provider Breadth / Coverage

Status: **COMPLETE**

Contract:

```text
DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_COVERAGE_V1
```

User-executed test result:

```text
10 tests
OK
```

Probe generated at `2026-09-03T06:12:06.866159+00:00`.

## Source reproducibility

SportsDataverse roster release manifest was acquired successfully. The 2024 and 2025 selected roster assets both matched their advertised SHA-256 digests.

```text
2024 asset: cfb_rosters_2024.csv.gz
sha256: ee3f18de4f3f9e585273ebbd39ac3b0ed020e2e7921b71cff1a061417d3bc083
advertised digest match: true

2025 asset: cfb_rosters_2025.csv.gz
sha256: f5d0641f8a67a5aa0d331b3c2bd3f98aef5800d6e446cf86261e3bbf44793948
advertised digest match: true
```

## Deterministic breadth sample

Measured 13 FBS team-season slices spanning conference, independent, service-academy, realignment and recent-FBS-entry contexts.

```text
2024: Clemson, Michigan, Utah, Georgia, Army, Kennesaw State,
      Toledo, Boise State, App State, Oregon State, Notre Dame
2025: Delaware, Missouri State
```

All 13 slices returned non-empty rosters from both providers.

## Aggregate evidence

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

## Complete exact-set slices

```text
App State 2024       120 / 120
Oregon State 2024    114 / 114
Delaware 2025        111 / 111
Missouri State 2025  105 / 105
```

The two 2025 FBS entrants both produced exact cross-provider roster ID-set equality in the measured season.

## Lowest-coverage slices

### Georgia 2024

```text
CFBD IDs       137
ESPN IDs       132
shared         129
CFBD-only        8
ESPN-only        3
CFBD overlap  94.1606%
ESPN overlap  97.7273%
```

### Utah 2024

```text
CFBD IDs       110
ESPN IDs       123
shared         109
CFBD-only        1
ESPN-only       14
CFBD overlap  99.0909%
ESPN overlap  88.6179%
```

Neither slice contained duplicate athlete IDs. Provider-only rows remain coverage differences; they are not converted into identity disagreements.

## Name evidence

Same exact athlete IDs continued to appear under provider display-name differences, including examples such as:

```text
Tyshawn Sanders / Ty Sanders
Cameron Camper / Cam Camper
Tre Williams / Tré Williams
Tommy Doman / Tommy Doman Jr.
Reginald Johnson / RJ Johnson III
Sky Sholder / Skyler Sholder
```

Locked:

```text
name inequality != identity break
```

## C3-A + C3-B combined FBS evidence

Across the 22 FBS team-season slices measured by C3-A and C3-B:

```text
CFBD unique athlete-ID observations       2745
ESPN unique athlete-ID observations       2749
exact shared athlete-ID observations      2715
combined weighted CFBD overlap          98.9071%
combined weighted ESPN overlap          98.7632%
```

The combined value is an observation-count aggregate across slices, not a count of globally unique persons across seasons.

## Interpretation

C3-B satisfies the C3 freeze criteria.

The measured evidence strongly supports a shared recent-FBS external athlete-ID namespace between CFBD roster IDs and ESPN-derived `athlete_id` values. It does **not** establish equal roster coverage or population completeness.

Locked:

```text
shared external athlete ID = strong provider-crosswalk identity evidence
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
missing provider roster row != player absence
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
classification/program membership != player identity
shared cross-provider ID != historical PIT safety
```

The Jackson State 2022 zero-ESPN-row case from C3-A remains an explicit FCS source-coverage limitation and is not contradicted by this FBS breadth pass.
