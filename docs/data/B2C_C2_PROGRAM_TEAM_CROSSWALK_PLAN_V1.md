# B.2-C C2 — Program / Team Provider Crosswalk Plan V1

Status: **ACTIVE**

Prerequisite: `B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md` is frozen.

## Objective

Determine whether CFBD team IDs and ESPN/SportsDataverse team IDs can be used as strong direct provider crosswalk evidence across completed seasons, while preserving Daily-NCAAF canonical `PROGRAM` identity independently of either provider.

C2 must answer:

1. Does each FBS program returned by `GET /teams/fbs?year=` appear in the participant-aligned ESPN schedule crosswalk for the same completed season?
2. When exactly one ESPN team ID is derived for a CFBD program, does it equal CFBD's own team `id`?
3. Does a stable CFBD program name retain one provider ID across seasons?
4. Does one provider ID ever map to multiple CFBD names across seasons, indicating rename/evolution evidence requiring explicit treatment?
5. Do FBS entry/exit transitions remain membership-state changes rather than identity changes?

## Initial completed-season window

```text
2023
2024
2025
```

These seasons deliberately span recent FBS membership transitions while avoiding treating the partial 2026 SportsDataverse schedule as final coverage evidence.

2026 remains a current-state observation and may be added later only as a snapshot stratum.

## Inputs

### CFBD

- `GET /teams/fbs?year=<season>`
- `GET /games?year=<season>&seasonType=both&classification=fbs` through the frozen C1 reconciliation harness

### SportsDataverse / ESPN

- manifest-discovered `espn_cfb_schedules` season asset
- exact event IDs and participant-aligned ESPN team IDs through C1 V4 semantics

## Required per-season evidence

```text
FBS team rows
unique CFBD school names
unique CFBD team IDs
duplicate school names
duplicate team IDs
participant-derived ESPN crosswalk coverage
FBS schools missing schedule-derived crosswalk
CFBD team-ID == derived ESPN team-ID count
CFBD team-ID != derived ESPN team-ID examples
within-season CFBD-name -> multiple ESPN-ID conflicts
within-season ESPN-ID -> multiple CFBD-name conflicts
```

## Required cross-season evidence

For each observed FBS school name:

```text
seasons observed
CFBD IDs observed
ESPN IDs observed
display names observed
```

Report separately:

```text
same CFBD name -> multiple provider IDs
same ESPN ID -> multiple CFBD names
same CFBD ID -> multiple CFBD names
```

Multiple names on one stable provider ID are **name-evolution candidates**, not automatic canonical merges.

## Membership transitions

For each adjacent season pair report:

```text
entered_fbs
exited_fbs
```

Locked interpretation:

```text
FBS membership change != new PROGRAM identity
classification stint != provider team identity
```

## C2 safety rules

```text
provider team ID != canonical PROGRAM_ID
name equality != canonical identity proof
name inequality != identity break
classification change != identity break
same provider ID + changed name = investigate/record evolution; do not silently rewrite history
```

## C2 freeze candidate criteria

C2 can become a freeze candidate if completed 2023–2025 demonstrate:

1. complete or explicitly explained FBS schedule-derived crosswalk coverage;
2. no unresolved within-season team-ID collisions;
3. direct CFBD team IDs agree with independently derived ESPN IDs wherever both are present, or every disagreement is individually explained;
4. cross-season ID changes/renames are surfaced explicitly rather than hidden by normalization;
5. membership transitions are represented separately from identity.

C2 does not make either provider's ID canonical. It establishes provider-crosswalk strength and the evidence needed for the Phase C `PROGRAM_PROVIDER_CROSSWALK` contract.