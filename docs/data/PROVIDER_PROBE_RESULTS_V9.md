# Daily NCAAF — Provider Probe Results V9

**Phase:** B.2-B — CFBD Targeted Identity & Scope  
**Status:** POSITIVE PLAYER/TRANSFER/COACH CONTINUITY CASES COMPLETE; missing-link/collision cases next  
**Probe generated:** 2026-08-31T08:15:06Z  
**Harness contract:** `DAILY_NCAAF_PHASE_B2_CFBD_IDENTITY_CASE_PROBE_V1`

---

## 1. Purpose

This document records bounded CFBD identity-continuity cases designed to test whether provider player and coach identifiers survive time, school changes, transfers, and classification changes.

Local test result before execution:

```text
Ran 9 tests in 0.001s
OK
```

The probe used normalized names only to locate candidate rows. Name equality was never promoted to canonical identity.

---

## P-054 — CFBD roster athlete IDs are stable in the measured same-program case

### Jalen Milroe

Observed roster identity:

```text
CFBD athlete ID: 4432734
Alabama 2021 -> 4432734
Alabama 2022 -> 4432734
Alabama 2023 -> 4432734
Alabama 2024 -> 4432734
```

The 2021 recruiting record also exposed:

```text
athleteId = 4432734
```

which directly matched the roster identifier.

Measured interpretation:

```text
recruit -> roster = DIRECT_PROVIDER_LINK
roster multi-season identity = STABLE_PROVIDER_ID
```

This supports CFBD athlete IDs as strong provider crosswalk evidence.

It does **not** make a provider ID the canonical Daily-NCAAF player identity.

---

## P-055 — CFBD roster athlete ID survives multiple FBS transfers

### Dillon Gabriel

One provider athlete ID persisted across six measured roster-season observations and three programs:

```text
CFBD athlete ID: 4427238

UCF       2019 -> 4427238
UCF       2020 -> 4427238
UCF       2021 -> 4427238
Oklahoma  2022 -> 4427238
Oklahoma  2023 -> 4427238
Oregon    2024 -> 4427238
```

The 2019 recruiting record exposed the same `athleteId`.

The portal family returned two contextual transfer rows:

```text
UCF -> Oklahoma
Oklahoma -> Oregon
```

but those portal rows exposed no player/athlete identifier in the measured schema.

Locked consequence:

```text
TRANSFER DOES NOT CREATE A NEW PLAYER IDENTITY
```

and:

```text
portal row != canonical player identity source
```

The canonical architecture remains:

```text
PERSON
  -> PLAYER
      -> PLAYER_PROGRAM_STINT 1
      -> PLAYER_PROGRAM_STINT 2
      -> PLAYER_PROGRAM_STINT 3
```

with provider athlete IDs stored as crosswalk evidence.

---

## P-056 — CFBD athlete ID survives an FCS -> FBS move

### Travis Hunter

Observed:

```text
CFBD athlete ID: 4685415

Jackson State 2022 (FCS) -> 4685415
Colorado      2023 (FBS) -> 4685415
Colorado      2024 (FBS) -> 4685415
```

The recruiting record also exposed:

```text
athleteId = 4685415
committedTo = Jackson State
```

and the 2023 portal-family observation supplied contextual evidence:

```text
origin      = Jackson State
destination = Colorado
transferDate = 2022-12-19T04:36:00Z
```

Again, the portal row itself exposed no explicit athlete identifier.

Locked consequence:

```text
classification change != new player identity
```

Canonical player continuity must survive FCS/FBS boundaries.

---

## P-057 — Modern single-transfer case shows the same split between strong roster IDs and ID-less portal context

### Caleb Downs

Observed:

```text
CFBD athlete ID: 4870706

Alabama    2023 -> 4870706
Ohio State 2024 -> 4870706
Ohio State 2025 -> 4870706
```

The recruiting record exposed the same `athleteId` and the portal row recorded:

```text
Alabama -> Ohio State
transferDate = 2024-01-17T15:39:00Z
```

The transfer row again had no explicit player identifier.

This independently reproduces the Gabriel/Hunter pattern.

---

## P-058 — Portal records are transfer observations, not standalone player identities

Across the measured transfer cases:

```text
Dillon Gabriel: 2 portal rows, 0 explicit player identifiers
Travis Hunter:  1 portal row,  0 explicit player identifiers
Caleb Downs:    1 portal row,  0 explicit player identifiers
```

The observed portal schema keys were contextual fields such as:

```text
firstName
lastName
origin
destination
position
rating
stars
eligibility
transferDate
season
```

No measured portal candidate exposed `id` or `athleteId`.

Therefore the Phase C contract must model a portal row as something like:

```text
TRANSFER_OBSERVATION
  provider
  provider_record_identity/hash
  observed_name
  origin_program_evidence
  destination_program_evidence
  transfer_effective_at
  rating/stars/eligibility evidence
  acquired_at
  player_reconciliation_status
```

rather than embedding the portal row directly into `PLAYER` identity.

Allowed reconciliation outcomes remain:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

Name + origin + destination is evidence, not a universal primary key.

---

## P-059 — Coach provider IDs remain stable across program changes in the measured cases

### Nick Saban

One CFBD coach ID represented the measured college head-coaching career across:

```text
provider coach ID = 406
Toledo
Michigan State
LSU
Alabama
```

with 28 nested season entries from 1990 through 2023.

### Kalen DeBoer

```text
provider coach ID = 564
Fresno State
Washington
Alabama
```

with seven nested seasons from 2020 through 2026.

### Curt Cignetti

```text
provider coach ID = 1741
James Madison
Indiana
```

with five nested seasons from 2022 through 2026.

Measured verdict:

```text
CFBD coach ID = strong provider person/coach crosswalk candidate
school change != new coach identity
```

Daily-NCAAF still owns canonical `PERSON -> COACH -> COACH_ROLE_STINT` identity.

The `/coaches` family does not solve coordinator/play-caller history.

---

## P-060 — Provider roster row `year` must not be assumed to be the season key

The probe stores the requested roster season outside the returned row. Within the returned candidate rows, the provider field named `year` remained constant for a player across multiple requested seasons in several cases, e.g.:

```text
Jalen Milroe: returned row year = 3 across requested seasons 2021-2024
Dillon Gabriel: returned row year = 4 across requested seasons 2019-2024
Caleb Downs: returned row year = 3 across requested seasons 2023-2025
Travis Hunter: returned row year = 3 across requested seasons 2022-2024
```

Therefore:

```text
roster payload field `year` != safely interpretable as roster season
```

until its exact provider semantics are explicitly contracted.

Locked implementation consequence:

```text
query/requested season must be stored explicitly as observation context
```

Provider field names must not silently define canonical semantics.

---

## P-061 — Coach nested season payload mixes identity history with derived season metrics

The coach response nests school/year history together with fields such as:

```text
wins/losses
preseasonRank/postseasonRank
SP offense/defense/overall
SRS
```

Those metrics are not coach identity fields and may have retrospective/current-model semantics.

The canonical coach ingestion contract must separate:

```text
coach identity / role-stint evidence
```

from:

```text
season results / external ratings / retrospective derived metrics
```

No wholesale `/coaches` object should become a canonical coach row.

---

## B.2-B positive-identity verdict

The positive continuity cases are complete enough to lock the following:

1. CFBD roster athlete IDs are strong player crosswalk candidates;
2. measured athlete IDs survive multi-season state, FBS transfers, and FCS->FBS classification changes;
3. recruiting `athleteId` can directly bridge recruit and roster identities when present;
4. portal rows provide valuable transfer-state evidence but no explicit player ID in the measured schema;
5. CFBD coach IDs are strong coach crosswalk candidates across school changes;
6. provider response objects mix identity evidence with other semantics and must be normalized field-by-field;
7. provider IDs remain crosswalks, never canonical Daily-NCAAF identity.

The remaining B.2-B identity question is deliberately negative/hard-case evidence:

```text
recruiting row with athleteId = null
-> can roster recruitIds recover a direct provider link?
-> when it cannot, how often does exact-name context remain ambiguous?
```

That is the next targeted probe before B.2-C cross-provider reconciliation.
