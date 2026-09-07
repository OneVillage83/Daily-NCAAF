# B.2-C Provider Provenance Addendum V1

Status: **ACTIVE GOVERNING ADDENDUM**
Date: 2026-09-03

## Why this addendum exists

The B.2-C reconciliation work has compared CFBD API observations with SportsDataverse/cfbfastR ESPN-derived artifacts. Current SportsDataverse build documentation now states explicitly that its unified schedule producer treats the CollegeFootballData `/games` path as **ESPN data redistributed through CFBD**, while its native schedule artifact is sourced directly from ESPN.

Therefore the already-frozen C1-C4 results remain valid for:

```text
identifier compatibility
coverage reconciliation
delivery-path differences
source snapshot differences
provider/API contract differences
normalization rules
identity safety rules
```

But they must **not** be described as independent-source corroboration of underlying football truth.

## Frozen provenance interpretation

For the measured schedule/game ecosystem:

```text
CFBD /games delivery path
        -> ESPN-origin data redistributed by CFBD

SportsDataverse espn_cfb_schedules
        -> ESPN-native derived artifact
```

The paths may differ in:

```text
coverage
publication/update cadence
snapshot age
normalization
field availability
field semantics
revision state
```

They are nevertheless not independent upstream authorities.

## Effect on C1-C4

No freeze is invalidated.

C1 still proves the measured external event-ID namespace, participant reconciliation rules, home/away non-authority, and delivery-path coverage behavior.

C2 still proves external team-ID compatibility across the measured FBS window.

C3 still proves external athlete-ID compatibility and source-specific roster coverage behavior.

C4 still proves how identifier-less portal context must be reconciled against surrounding direct athlete-ID evidence.

What changes is the wording of the evidentiary strength:

```text
WRONG:
independent sources independently confirmed the same identity

CORRECT:
multiple delivery paths in the ESPN-origin ecosystem exposed compatible identifiers / observations
```

## Phase C requirement

Production provenance must distinguish at least:

```text
provider / delivery source
upstream authority / origin when known
retrieval endpoint or artifact
acquired_at
source hash
record hash
revision/version metadata
```

A future truly independent source may corroborate ESPN-origin observations, but that confirmation must be recorded as separate provenance rather than inferred from CFBD-vs-SportsDataverse agreement.

## C5 implication

C5 venue/conference/context reconciliation will explicitly test **delivery-path agreement**, not independent truth confirmation.

Provider disagreement remains useful because it reveals normalization, timing, coverage, and semantic differences even when the upstream origin is shared.
