# B.2-C C4 — Transfer-Event Reconciliation Freeze V1

Status: **COMPLETE / FROZEN**
Date: 2026-09-03

## Prerequisites

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3 player cross-provider identity — COMPLETE/FROZEN

## Freeze evidence

```text
user-executed tests: 10 / 10 OK
portal target events: 4
unique contextual portal candidate per event: 4 / 4
portal transferDate MATCH: 4 / 4
identifier conflicts: 0
portal ambiguity: 0
portal context missing: 0
```

Reconciliation states:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
```

Detailed evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V18.md
```

## Frozen transfer cases

### Dillon Gabriel — UCF -> Oklahoma

External athlete ID `4427238` appears directly in both CFBD and ESPN-derived rosters on the 2021 UCF origin side and 2022 Oklahoma destination side. The unique 2022 portal candidate states UCF -> Oklahoma and has the measured transfer-time observation `2021-11-27T07:07:00.000Z`.

State:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

### Dillon Gabriel — Oklahoma -> Oregon

External athlete ID `4427238` appears directly on both providers at Oklahoma 2023 and Oregon 2024. The unique portal candidate states Oklahoma -> Oregon and carries `2023-12-04T14:01:00.000Z`.

State:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

### Caleb Downs — Alabama -> Ohio State

External athlete ID `4870706` appears directly on both providers at Alabama 2023 and Ohio State 2024. The unique portal candidate states Alabama -> Ohio State and carries `2024-01-17T15:39:00.000Z`.

State:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

### Travis Hunter — Jackson State -> Colorado

External athlete ID `4685415` is directly present in the CFBD Jackson State 2022 roster and direct-shared in Colorado 2023. The ESPN-derived 2022 roster asset exposes zero Jackson State team rows, so the origin side cannot be independently observed within that delivery path.

The unique portal candidate states Jackson State -> Colorado and carries `2022-12-19T04:36:00.000Z`.

State:

```text
PARTIAL_DIRECT_SHARED_ID_BRACKET
```

This partial state is frozen as a source-coverage limitation, not an identity failure.

## Frozen production semantics

Canonical concepts remain separate:

```text
PLAYER
PLAYER_PROGRAM_STINT
TRANSFER_OBSERVATION
TRANSFER_RECONCILIATION
```

`TRANSFER_OBSERVATION` must preserve source evidence such as:

```text
provider
provider_record_hash
portal_season
observed_name
observed_origin
observed_destination
transfer_effective_time
rating
stars
eligibility
acquired_at
```

`TRANSFER_RECONCILIATION` must preserve:

```text
canonical/player target nullable
reconciliation state
method
confidence
origin evidence refs
destination evidence refs
portal evidence ref
review status
version
```

## Frozen safety rules

```text
portal row != PLAYER identity
portal name match != identity proof
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
same player + transfer != new PLAYER
missing source roster != player absence
partial bracket != identity conflict
transferDate != publication time
transferDate != acquired_at
```

Historical PIT use of portal observations remains blocked unless actual historical availability/publication evidence is defensible.

## Exit

C4 satisfies its freeze criteria. B.2-C advances to C5 venue/conference/context reconciliation.
