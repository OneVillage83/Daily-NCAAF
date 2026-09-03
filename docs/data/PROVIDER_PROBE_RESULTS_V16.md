# Provider Probe Results V16 — C3-A Player Cross-Provider Identity

Status: **C3-A COMPLETE; C3-B BREADTH PASS REQUIRED BEFORE GLOBAL C3 FREEZE**

Measured contract:

```text
DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_IDENTITY_V1
```

User-executed unit suite:

```text
11 tests
OK
```

## Executive finding

The measured CFBD roster athlete IDs and ESPN-derived SportsDataverse roster `athlete_id` values clearly use the same external athlete-ID namespace for recent FBS observations.

Across the nine measured FBS team-season roster slices:

```text
CFBD unique athlete IDs                     1111
ESPN unique athlete IDs                     1111
exact shared athlete IDs                    1099
CFBD-only athlete IDs                         12
ESPN-only athlete IDs                         12
weighted CFBD exact-ID overlap            98.92%
weighted ESPN exact-ID overlap            98.92%
```

No measured FBS slice contained duplicate athlete IDs on either provider side.

This establishes strong identifier compatibility. It does **not** establish complete roster coverage, because provider-only rows remain real observations and the sampled population is still targeted around the continuity cases.

## Target continuity cases

### Jalen Milroe

```text
expected athlete ID 4432734
2023 Alabama  DIRECT_SHARED_PROVIDER_ID
2024 Alabama  DIRECT_SHARED_PROVIDER_ID
```

Result:

```text
DIRECT_SHARED_PROVIDER_ID_ACROSS_ALL_MEASURED_STINTS
```

### Dillon Gabriel

```text
expected athlete ID 4427238
2022 Oklahoma  DIRECT_SHARED_PROVIDER_ID
2023 Oklahoma  DIRECT_SHARED_PROVIDER_ID
2024 Oregon    DIRECT_SHARED_PROVIDER_ID
```

Result:

```text
DIRECT_SHARED_PROVIDER_ID_ACROSS_ALL_MEASURED_STINTS
```

The same external athlete ID survives an FBS program transfer in both providers.

### Caleb Downs

```text
expected athlete ID 4870706
2023 Alabama     DIRECT_SHARED_PROVIDER_ID
2024 Ohio State  DIRECT_SHARED_PROVIDER_ID
2025 Ohio State  DIRECT_SHARED_PROVIDER_ID
```

Result:

```text
DIRECT_SHARED_PROVIDER_ID_ACROSS_ALL_MEASURED_STINTS
```

The same external athlete ID survives an FBS program transfer and remains stable after the transfer.

### Travis Hunter

```text
expected athlete ID 4685415
2022 Jackson State  CFBD_ONLY_IDENTIFIER
2023 Colorado       DIRECT_SHARED_PROVIDER_ID
2024 Colorado       DIRECT_SHARED_PROVIDER_ID
```

Result:

```text
PARTIAL_DIRECT_SHARED_PROVIDER_ID
```

Critically, the 2022 Jackson State result is **not an identifier disagreement**. The SportsDataverse 2022 roster asset returned zero rows for external team ID `2296`, while CFBD returned 119 Jackson State roster rows including Hunter.

Locked interpretation:

```text
ZERO SPORTS DATAVERSE TEAM ROWS != PLAYER ABSENCE
CFBD_ONLY_IDENTIFIER UNDER ZERO TEAM COVERAGE != IDENTITY CONFLICT
```

The FCS -> FBS continuity remains proven inside CFBD from B.2-B and is directly shared across both providers once Hunter is observed at Colorado. Cross-provider proof of the 2022 FCS stint itself remains unavailable from this source snapshot.

## FBS slice results

```text
2022 Oklahoma      CFBD 120  ESPN 118  shared 117
2023 Alabama       CFBD 138  ESPN 141  shared 138
2023 Colorado      CFBD 113  ESPN 115  shared 113
2023 Oklahoma      CFBD 125  ESPN 124  shared 124
2024 Alabama       CFBD 133  ESPN 133  shared 133
2024 Colorado      CFBD 113  ESPN 111  shared 108
2024 Ohio State    CFBD 123  ESPN 123  shared 122
2024 Oregon        CFBD 126  ESPN 126  shared 124
2025 Ohio State    CFBD 120  ESPN 120  shared 120
```

Per-slice exact-ID overlap remained high across every measured FBS team-season. Complete set equality occurred for 2024 Alabama and 2025 Ohio State. The lowest measured CFBD-side overlap was 95.5752% for 2024 Colorado; the lowest ESPN-side overlap was 97.2973% for that same slice.

Provider-only IDs must remain explicit coverage differences rather than being auto-merged by name.

## Same ID, different display text

The audit produced many examples where the exact same athlete ID carried different provider display text, including:

```text
4240333  C.J. Coldon        / C.J. Coldon Jr.
4426484  Marcus Major       / Marcus Major Jr.
4686472  Marvin Mims        / Marvin Mims Jr.
4373909  Leonard Payne Jr.  / Leonard Payne
4686768  Gerad Christian-Lichtenhan / Gerad Lichtenhan
4566154  JT Tuimoloau       / Jaylahn Tuimoloau
5079586  JacQawn McRoy      / Shaq McRoy
5130407  Roger Saleapaga II / Roger Saleapaga
5081999  CJ Donaldson Jr    / CJ Donaldson
```

Locked:

```text
name inequality != identity break
same external athlete ID can survive name/display evolution
position-label inequality can also be provider taxonomy rather than identity disagreement
```

Names remain diagnostics only.

## SportsDataverse source evidence

The roster release manifest was acquired successfully and the measured 2022-2025 assets all passed advertised SHA-256 digest verification.

Measured assets:

```text
cfb_rosters_2022.csv.gz
cfb_rosters_2023.csv.gz
cfb_rosters_2024.csv.gz
cfb_rosters_2025.csv.gz
```

Each acquisition retains asset update time, source URL, byte count, SHA-256, advertised digest and `acquired_at`.

## C3-A conclusion

C3-A establishes:

```text
recent FBS CFBD roster athlete ID == ESPN-derived athlete_id namespace
```

as strong cross-provider identity evidence.

It does **not** establish:

```text
provider athlete ID == canonical Daily-NCAAF PLAYER_ID
provider roster coverage == complete player population
missing provider row == player absence
shared provider ID == historical PIT safety
```

## Why C3-B still runs

The C3 plan explicitly requires a breadth expansion when targeted continuity succeeds but provider-only IDs remain. The nine FBS slices were selected around four continuity anchors and therefore are not sufficiently representative to freeze population coverage assumptions.

C3-B will add a deterministic breadth sample spanning current conference strata, independent programs, a service-academy case, a recent FBS entrant and 2025 entrants. It will quantify whether the ~99% exact-ID overlap persists outside the original target programs.
