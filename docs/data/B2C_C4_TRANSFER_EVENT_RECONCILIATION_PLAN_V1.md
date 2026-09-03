# B.2-C C4 — Transfer-Event Reconciliation Plan V1

Status: **ACTIVE**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team crosswalk — COMPLETE/FROZEN
- C3 player cross-provider identity — COMPLETE/FROZEN

## Objective

Reconcile CFBD transfer-portal observations against frozen player/program identities and surrounding CFBD + ESPN-derived roster stints without allowing identifier-less portal rows to become identity authority.

C4 must answer:

1. Can a portal observation be bracketed by the same direct external athlete ID before and after an FBS transfer?
2. Do origin/destination context and portal season/date agree with the observed program-stint transition?
3. What happens when one surrounding provider roster is absent, as in the measured Jackson State 2022 SportsDataverse gap?
4. Can multiple portal rows with the same normalized name/origin/destination create ambiguity?
5. Which transfer fields are event/context evidence versus player identity evidence?

## Locked prerequisite from B.2-B

Measured CFBD portal rows exposed fields such as:

```text
season
firstName
lastName
position
origin
destination
transferDate
rating
stars
eligibility
```

The measured portal schema did **not** expose a direct player/athlete identifier.

Therefore:

```text
portal row != canonical PLAYER identity
portal name != identity key
```

## Target transfer events

### Dillon Gabriel — UCF -> Oklahoma

```text
portal season: 2022
expected athlete id: 4427238
origin roster: UCF 2021
next roster: Oklahoma 2022
measured transferDate: 2021-11-27T07:07:00.000Z
```

### Dillon Gabriel — Oklahoma -> Oregon

```text
portal season: 2024
expected athlete id: 4427238
origin roster: Oklahoma 2023
next roster: Oregon 2024
measured transferDate: 2023-12-04T14:01:00.000Z
```

### Travis Hunter — Jackson State -> Colorado

```text
portal season: 2023
expected athlete id: 4685415
origin roster: Jackson State 2022 (FCS)
next roster: Colorado 2023
measured transferDate: 2022-12-19T04:36:00.000Z
```

The ESPN-derived Jackson State 2022 roster is already known to be absent. C4 must preserve this as a coverage state rather than treating the origin player as missing.

### Caleb Downs — Alabama -> Ohio State

```text
portal season: 2024
expected athlete id: 4870706
origin roster: Alabama 2023
next roster: Ohio State 2024
measured transferDate: 2024-01-17T15:39:00.000Z
```

## Inputs

CFBD:

```text
GET /player/portal?year=<portal season>
GET /roster?year=<season>&team=<program>&classification=<fbs|fcs>
```

SportsDataverse / ESPN-derived:

```text
espn_cfb_rosters season assets
```

C2 external program/team IDs and C3 athlete-ID crosswalk semantics are prerequisites.

## Matching hierarchy

Portal rows are found using contextual evidence only:

```text
normalized player name
+ expected origin program
+ expected destination program
+ portal season
```

This does **not** establish canonical identity.

The player identity bracket comes from the expected athlete ID in surrounding roster observations.

## Required surrounding-stint states

For each origin and destination roster observation:

```text
DIRECT_SHARED_PROVIDER_ID
CFBD_ONLY_IDENTIFIER
ESPN_ONLY_IDENTIFIER
IDENTIFIER_DISAGREEMENT
UNRESOLVED
NO_ESPN_TEAM_ROWS
NO_CFBD_TEAM_ROWS
```

## Transfer-event reconciliation states

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET
PARTIAL_DIRECT_SHARED_ID_BRACKET
CFBD_ONLY_TWO_SIDED_ID_BRACKET
PORTAL_CONTEXT_AMBIGUOUS
PORTAL_CONTEXT_NOT_FOUND
IDENTIFIER_CONFLICT
UNRESOLVED
```

A two-sided bracket means the same expected external athlete ID is observed on both pre- and post-transfer program stints. It does not mean the portal row itself contains that ID.

## Portal observation contract

Canonical concept:

```text
TRANSFER_OBSERVATION
  provider
  provider_record_hash
  portal_season
  observed_name
  origin_program_evidence
  destination_program_evidence
  transfer_effective_time
  rating
  stars
  eligibility
  acquired_at
  player_reconciliation_status
  reconciled_player_id nullable
  reconciliation_method nullable
  evidence references
```

The canonical `PLAYER_PROGRAM_STINT` remains separate from the transfer observation.

## Safety rules

```text
portal name match != player identity
portal origin/destination != canonical stint by itself
transferDate != publication time
transferDate != acquired_at
same external athlete ID across programs != new PLAYER
missing ESPN origin roster != transfer failure
provider-only row != identity conflict
```

## C4 freeze candidate criteria

C4 can freeze if:

1. measured FBS transfer cases are bracketed by the same athlete ID before/after without identifier conflicts;
2. portal context agrees with the measured origin/destination transition or any disagreement is explicit;
3. Hunter's FCS-origin coverage gap remains explicit rather than repaired by name;
4. ambiguous/missing portal contexts remain unresolved instead of auto-linked;
5. the production transfer observation contract separates portal evidence, player identity and program stints;
6. portal timestamps remain temporal observations and are not treated as publication/PIT timestamps.
