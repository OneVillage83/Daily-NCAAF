# B.2-C C3 — Player Cross-Provider Identity Plan V1

Status: **C3-A COMPLETE; C3-B ACTIVE**

Prerequisites:

- C1 game/event identity — frozen
- C2 program/team provider crosswalk — frozen

## Objective

Determine whether CFBD roster athlete identifiers and ESPN-derived SportsDataverse roster athlete identifiers provide strong direct cross-provider player identity evidence, including across transfers and an FCS→FBS movement, without using names as identity keys.

C3 must answer:

1. Do CFBD roster athlete IDs equal ESPN `athlete_id` values for the same measured player/team-season observations?
2. How much exact athlete-ID overlap exists for full roster slices?
3. Do the same athlete IDs survive program transfers across both providers?
4. Does the same athlete ID survive an FCS→FBS move across both providers where both sources actually expose the stint?
5. Are there provider-specific missing roster observations even when identity itself is stable?
6. Do display-name differences prove name-only matching remains unsafe?

## ESPN-derived source

SportsDataverse publishes `espn_cfb_rosters`, an ESPN-derived season roster compilation with identifier-bearing fields including:

```text
athlete_id
athlete_uid
athlete_guid
team_id
full_name / athlete display fields
```

Every acquired asset retains:

```text
asset name
asset updated_at
advertised digest
downloaded SHA-256
acquired_at
```

## C3-A — COMPLETE

Target continuity cases:

```text
Jalen Milroe     4432734
Dillon Gabriel   4427238
Travis Hunter    4685415
Caleb Downs      4870706
```

User-executed C3-A suite:

```text
11 tests
OK
```

Measured target states:

```text
Jalen Milroe
2023 Alabama  DIRECT_SHARED_PROVIDER_ID
2024 Alabama  DIRECT_SHARED_PROVIDER_ID

Dillon Gabriel
2022 Oklahoma  DIRECT_SHARED_PROVIDER_ID
2023 Oklahoma  DIRECT_SHARED_PROVIDER_ID
2024 Oregon    DIRECT_SHARED_PROVIDER_ID

Caleb Downs
2023 Alabama     DIRECT_SHARED_PROVIDER_ID
2024 Ohio State  DIRECT_SHARED_PROVIDER_ID
2025 Ohio State  DIRECT_SHARED_PROVIDER_ID

Travis Hunter
2022 Jackson State  CFBD_ONLY_IDENTIFIER
2023 Colorado       DIRECT_SHARED_PROVIDER_ID
2024 Colorado       DIRECT_SHARED_PROVIDER_ID
```

Gabriel and Downs therefore provide direct cross-provider evidence that the same external athlete ID survives FBS program transfers.

Hunter's 2022 Jackson State result is a source coverage gap, not an identifier disagreement: the SportsDataverse 2022 roster asset exposed zero rows for Jackson State team ID `2296`, while CFBD exposed 119 roster rows including Hunter.

Locked:

```text
ZERO PROVIDER TEAM ROWS != PLAYER ABSENCE
CFBD_ONLY_IDENTIFIER UNDER ZERO TEAM COVERAGE != IDENTITY CONFLICT
```

## C3-A surrounding FBS roster evidence

Across nine FBS team-season slices surrounding the targets:

```text
CFBD unique athlete IDs                  1111
ESPN unique athlete IDs                  1111
exact shared athlete IDs                 1099
CFBD-only athlete IDs                      12
ESPN-only athlete IDs                      12
weighted CFBD exact-ID overlap          98.92%
weighted ESPN exact-ID overlap          98.92%
```

No measured FBS slice contained duplicate athlete IDs on either provider side.

The same external athlete ID frequently survives display-name differences, including suffix, abbreviation and preferred-name variants. Therefore:

```text
name inequality != identity break
provider athlete display text != canonical identity
```

Detailed evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V16.md
```

Tooling:

```text
scripts/probes/cross_provider_player_identity_probe.py
tests/probes/test_cross_provider_player_identity_probe.py
```

## C3-B — ACTIVE breadth / coverage pass

C3-A establishes strong identifier compatibility but does not prove population-complete roster coverage. The initial FBS sample was concentrated around Alabama, Oklahoma, Colorado, Oregon and Ohio State.

C3-B therefore performs the plan's bounded expansion trigger across deterministic structural strata:

```text
2024 Clemson
2024 Michigan
2024 Utah
2024 Georgia
2024 Army
2024 Kennesaw State
2024 Toledo
2024 Boise State
2024 App State
2024 Oregon State
2024 Notre Dame
2025 Delaware
2025 Missouri State
```

This spans major conferences, Group-of-Five conferences, an independent, a service academy, conference realignment, a recent FBS entrant and the two 2025 FBS entrants measured in C2.

Plan:

```text
docs/data/B2C_C3_PLAYER_COVERAGE_BREADTH_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_player_coverage_probe.py
tests/probes/test_cross_provider_player_coverage_probe.py
```

C3-B measures per-slice and aggregate exact athlete-ID overlap, provider-only IDs, zero-team coverage and duplicate-ID behavior.

## Safety rules

```text
provider athlete ID != canonical PLAYER_ID
name equality != identity proof
name inequality != identity break
same player + transfer != new PLAYER
FCS -> FBS != new PLAYER
missing provider roster row != player absence
provider-only roster row != identity disagreement
shared cross-provider ID != historical PIT safety
```

## C3 freeze criteria

C3 may freeze only when:

1. targeted continuity cases are resolved with explicit identifier evidence or explicit unresolved/coverage states;
2. no identifier disagreement is silently repaired by name;
3. a broader deterministic FBS sample demonstrates a dominant shared identifier namespace without unexplained collisions;
4. provider-only roster rows remain explicit coverage differences;
5. transfer continuity is separated from program-stint state;
6. remaining FCS/source coverage gaps are explicit rather than interpreted as player absence;
7. canonical Daily-NCAAF `PLAYER_ID` remains independent from provider IDs.
