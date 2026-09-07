# B.2-C C2 — Program / Team Provider Crosswalk Plan V1

Status: **COMPLETE / FROZEN**

Prerequisite: `B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md` is frozen.

Freeze authority: `B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md`.

## Objective

Determine whether CFBD team IDs and ESPN/SportsDataverse team IDs can be used as strong direct provider crosswalk evidence across completed seasons, while preserving Daily-NCAAF canonical `PROGRAM` identity independently of either provider.

## Audited completed-season window

```text
2023
2024
2025
```

2026 was intentionally excluded from the completed-season freeze because its SportsDataverse schedule remained an acquisition-state subset.

## Completed result

The probe passed all 11 tests and measured:

```text
2023: 133 / 133 FBS programs mapped; 133 direct ID matches
2024: 134 / 134 FBS programs mapped; 134 direct ID matches
2025: 136 / 136 FBS programs mapped; 136 direct ID matches
```

Every mapped CFBD `/teams/fbs` team `id` equaled the independently derived ESPN `team_id`.

Across the full window:

```text
unique FBS school names                         136
unique CFBD team IDs                            136
unique ESPN team IDs                            136
same CFBD school -> multiple provider IDs         0
same ESPN ID -> multiple CFBD names               0
same CFBD ID -> multiple CFBD names               0
```

## Membership transitions

```text
2023 -> 2024
entered_fbs: Kennesaw State
exited_fbs: none

2024 -> 2025
entered_fbs: Delaware, Missouri State
exited_fbs: none
```

Locked interpretation:

```text
FBS membership change != new PROGRAM identity
classification stint != provider team identity
```

## Display-name evolution

One measured example retained external team ID `2026` while ESPN display text evolved from `Appalachian State Mountaineers` to `App State Mountaineers`.

Locked:

```text
provider display-name change != identity change
name equality != canonical identity proof
name inequality != identity break
```

## Frozen provider-ID interpretation

For the measured 2023-2025 FBS universe:

```text
CFBD team id == ESPN team id
```

This is strong evidence of a shared external numeric team-ID namespace in the audited window.

It does **not** make the external ID canonical Daily-NCAAF identity.

```text
provider team ID != canonical PROGRAM_ID
```

Source provenance remains mandatory even when two sources expose the same external value.

## Phase C consequence

Minimum provider-independent program identity architecture remains:

```text
PROGRAM
PROGRAM_SEASON
CLASSIFICATION_STINT
CONFERENCE_AFFILIATION_STINT
PROGRAM_PROVIDER_IDENTIFIER / PROVIDER_IDENTIFIER_OBSERVATION
```

Provider-identifier observations retain namespace, value, source, acquired-at evidence and valid intervals where defensible.

## Freeze evidence

- `PROVIDER_PROBE_RESULTS_V15.md`
- `B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md`
- `scripts/probes/cross_provider_team_crosswalk_probe.py`
- `tests/probes/test_cross_provider_team_crosswalk_probe.py`

All predeclared C2 freeze criteria passed.

## Next gate

**B.2-C C3 — player cross-provider identity** is active.
