# B.2-C C4 — Transfer-Event Reconciliation Plan V1

Status: **COMPLETE / FROZEN**

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

```text
Dillon Gabriel  UCF 2021 -> Oklahoma 2022
Dillon Gabriel  Oklahoma 2023 -> Oregon 2024
Travis Hunter   Jackson State 2022 -> Colorado 2023
Caleb Downs     Alabama 2023 -> Ohio State 2024
```

## Matching hierarchy

Portal rows are found using contextual evidence only:

```text
normalized player name
+ expected origin program
+ expected destination program
+ portal season
```

This does **not** establish canonical identity. The player identity bracket comes from the expected athlete ID in surrounding roster observations.

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

## User-executed completion evidence

```text
unit tests: 10
result: OK
portal target events: 4
unique portal candidate per event: 4 / 4
portal transferDate MATCH: 4 / 4
```

Final reconciliation states:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

The three all-FBS cases bracketed the same direct shared athlete ID on both sides. Travis Hunter remained intentionally partial because SportsDataverse exposes zero Jackson State 2022 roster rows while CFBD directly exposes athlete ID `4685415` there and both paths expose the same ID at Colorado in 2023.

Detailed evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V18.md
docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_FREEZE_V1.md
```

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

## Frozen safety rules

```text
portal name match != player identity
portal origin/destination != canonical stint by itself
transferDate != publication time
transferDate != acquired_at
same external athlete ID across programs != new PLAYER
missing ESPN origin roster != transfer failure
partial bracket != identity conflict
provider-only row != identity conflict
```

## Exit

All predeclared C4 freeze criteria are satisfied. C4 is COMPLETE/FROZEN and B.2-C advances to C5 venue/conference/context reconciliation.
