# Daily NCAAF — CFBD Targeted Identity & Scope Plan V1

**Phase:** B.2-B  
**Status:** ACTIVE  
**Precondition:** broad CFBD annual family/era scan complete through 2025

---

## 1. Why the work changes here

Broad endpoint discovery has reached diminishing returns. The remaining questions are no longer "does CFBD expose this family?" They are:

- what exact entity universe does a family represent by season;
- how reliably do provider IDs preserve player/coach identity through time;
- where are direct links missing and reconciliation required;
- which state fields are retrospective truth versus historical knowledge state.

Therefore B.2-B now moves from broad annual scans to bounded identity/scope case studies.

---

## 2. Target A — talent membership scope

Research harness:

```text
scripts/probes/cfbd_talent_scope_probe.py
```

Test contract:

```text
tests/probes/test_cfbd_talent_scope_probe.py
```

Target seasons:

```text
2023
2024
2025
2026
```

Compare exact provider names returned by:

```text
GET /teams/fbs?year=<season>
GET /talent?year=<season>
```

Measure:

- FBS row/name count;
- talent row/name count;
- duplicate names;
- exact-name overlap;
- FBS programs absent from talent;
- talent programs outside the FBS membership list;
- exact membership match boolean.

The first pass deliberately does **not** fuzzy-normalize names. Provider alias/name differences should be surfaced as reconciliation evidence rather than silently hidden.

### Reliability behavior

The targeted harness includes:

- default request pacing;
- bounded retry on HTTP 429;
- `Retry-After` support where available;
- explicit HTTP/error state;
- no API-key output.

This is research tooling, not production acquisition.

---

## 3. Target B — player identity continuity

After talent scope is measured, choose bounded real player cases covering:

### B1. Same-program multi-season player

Measure whether the CFBD athlete ID remains stable across:

- seasons;
- jersey changes;
- position changes;
- roster metadata changes.

### B2. Single-transfer player

Trace:

```text
recruiting record
-> college athlete/player identity
-> origin roster
-> portal observation
-> destination roster
```

Record every link as:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

### B3. Multiple-transfer player

Verify that one player identity can own multiple chronological program stints without fragmentation.

### B4. Recruit with no athleteId

Select at least one recruiting row with no direct `athleteId` and test whether later roster evidence can be reconciled without name-only auto-merge.

### B5. FBS/FCS mover

Test continuity across classification boundaries.

### B6. Similar-name collision

Select a case where name-only matching would be unsafe and document the disambiguating evidence required.

---

## 4. Target C — coach identity continuity

Choose multiple coaches including at least:

- long-tenure same-program head coach;
- coach who changes schools;
- interim/head-coach transition if represented.

Measure:

- provider coach-ID stability;
- nested season behavior;
- team change representation;
- year filtering semantics;
- whether identity survives school change.

This work does not solve the separate OC/DC/play-caller historical gap.

---

## 5. Target D — rating entity normalization

No further broad rating harvesting is required before Phase C.

The architecture must preserve rating-family-specific state including:

```text
rating_family
provider_team_identity
division/classification when exposed
season
through_week / snapshot semantics
provider_model_version when exposed
acquired_at
PIT classification
```

Already locked:

- CORE: retrospective history starts in 2016; PIT-C by default.
- Elo: year-only query is latest-available-week, not an explicit weekly snapshot.
- SRS: broader entity universe from the observed 2022+ responses.
- SP+: near-FBS-sized but with repeated extra/null-conference behavior.
- FPI: strong FBS-aligned benchmark candidate, still requiring PIT provenance.

---

## 6. B.2-B exit criteria

B.2-B closes when:

1. talent membership scope is directly measured for 2023-2026;
2. representative player cases validate transfer-safe identity semantics;
3. missing recruit linkage is demonstrated without unsafe auto-merging;
4. representative coach continuity is measured;
5. provider-specific ambiguities are explicit enough to constrain Phase C canonical contracts.

Then advance to:

```text
B.2-C — CFBD <-> ESPN/cfbfastR cross-provider reconciliation
```

Do not return to broad annual endpoint scans unless a targeted case reveals a new unresolved era boundary.
