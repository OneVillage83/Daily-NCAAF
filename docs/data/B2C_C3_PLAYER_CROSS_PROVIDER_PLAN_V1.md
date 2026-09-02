# B.2-C C3 — Player Cross-Provider Identity Plan V1

Status: **ACTIVE**

Prerequisites:

- C1 game/event identity — frozen
- C2 program/team provider crosswalk — frozen

## Objective

Determine whether CFBD roster athlete identifiers and ESPN-derived SportsDataverse roster athlete identifiers provide strong direct cross-provider player identity evidence, including across transfers and an FCS→FBS movement, without using names as identity keys.

C3 must answer:

1. Do CFBD roster athlete IDs equal ESPN `athlete_id` values for the same measured player/team-season observations?
2. How much exact athlete-ID overlap exists for the full roster slices surrounding the targeted cases?
3. Do the same athlete IDs survive program transfers across both providers?
4. Does the same athlete ID survive an FCS→FBS move across both providers?
5. Are there provider-specific missing roster observations even when identity itself is stable?
6. Do name collisions or display differences exist that prove name-only matching remains unsafe?

## ESPN-derived source

SportsDataverse publishes `espn_cfb_rosters`, an ESPN-derived season roster compilation.

Its documented grain is one row per `(season, team_id, athlete_id)`, retaining identifier-bearing fields including:

```text
athlete_id
athlete_uid
athlete_guid
team_id
full_name / athlete display fields
```

The release is mutable and regenerated, so every acquired asset must retain:

```text
asset name
asset updated_at
advertised digest
downloaded SHA-256
acquired_at
```

## Initial targeted continuity cases

These reuse player identities already proven inside CFBD during B.2-B.

```text
Jalen Milroe
  CFBD athlete id 4432734
  Alabama 2023 -> Alabama 2024

Dillon Gabriel
  CFBD athlete id 4427238
  Oklahoma 2022 -> Oklahoma 2023 -> Oregon 2024

Travis Hunter
  CFBD athlete id 4685415
  Jackson State 2022 (FCS) -> Colorado 2023 -> Colorado 2024

Caleb Downs
  CFBD athlete id 4870706
  Alabama 2023 -> Ohio State 2024 -> Ohio State 2025
```

Names are allowed only to discover/diagnose candidate rows. The identifier comparison is authoritative for this audit.

## Team-ID anchors

C2 froze the shared external numeric team-ID namespace for measured FBS programs.

The targeted FBS anchors therefore use those frozen external IDs. Jackson State's external team ID is retained from prior exact-event participant evidence.

Provider team IDs remain external crosswalk evidence, not canonical `PROGRAM_ID` values.

## C3-A — targeted identity + surrounding roster slices

For every unique target team-season slice:

1. fetch CFBD `/roster` with explicit season/team/classification;
2. load the manifest-selected SportsDataverse roster asset for that season;
3. filter ESPN roster rows using the already established external team ID;
4. compare exact athlete-ID sets for the entire team-season slice;
5. inspect the target player's expected identifier in both sources;
6. retain name/position differences as diagnostics only.

Required slice evidence:

```text
CFBD roster rows
CFBD unique athlete IDs
ESPN roster rows
ESPN unique athlete IDs
exact shared athlete IDs
CFBD-only athlete IDs
ESPN-only athlete IDs
CFBD exact-ID overlap rate
duplicate IDs
same-ID name differences
```

Required target-case evidence:

```text
expected CFBD athlete ID
CFBD observation present?
ESPN observation present?
shared exact identifier?
team-season history by provider
cross-team continuity state
```

Identity states:

```text
DIRECT_SHARED_PROVIDER_ID
CFBD_ONLY_IDENTIFIER
ESPN_ONLY_IDENTIFIER
IDENTIFIER_DISAGREEMENT
AMBIGUOUS_NAME_CANDIDATES
UNRESOLVED
```

## C3-B — expansion trigger

Do not assume targeted success proves population completeness.

After C3-A:

- if surrounding roster-slice athlete-ID overlap is consistently strong and target continuity is clean, expand only as needed to quantify coverage/missingness across a broader deterministic program sample;
- if provider-only IDs or collisions are material, perform a dedicated coverage/collision pass before freezing C3.

## Safety rules

```text
provider athlete ID != canonical PLAYER_ID
name equality != identity proof
name inequality != identity break
same player + transfer != new PLAYER
FCS -> FBS != new PLAYER
missing provider roster row != player absence
shared cross-provider ID != historical PIT safety
```

## C3 freeze criteria

C3 may freeze only when:

1. the targeted continuity cases are resolved with explicit identifier evidence or explicit unresolved states;
2. no identifier disagreement is silently repaired by name;
3. surrounding roster-slice overlap/missingness is quantified well enough to define provider-independent player-crosswalk contracts;
4. transfer continuity is separated from program-stint state;
5. remaining source missingness is explicit rather than interpreted as player absence.
