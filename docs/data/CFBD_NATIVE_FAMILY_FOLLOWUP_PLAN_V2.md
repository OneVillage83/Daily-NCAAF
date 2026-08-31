# Daily NCAAF — CFBD Native-Family Follow-up Plan V2

**Phase:** B.2-B  
**Status:** ACTIVE  
**Supersedes:** `CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md` for the immediate next local work.

---

## 1. Why the plan is narrower now

The continuous 2015-2026 portal/talent/rating scan resolved most remaining broad era questions before temporary HTTP 429 responses interrupted the 2025/2026 tail.

Do **not** repeat the entire scan.

The immediate goals are now:

1. obtain one clean 2025 portal/talent/ratings observation;
2. compare talent-composite membership directly with the FBS program universe around the apparent 2023->2024 scope transition;
3. execute player/transfer/coach identity case studies;
4. then move into B.2-C CFBD <-> cfbfastR reconciliation.

---

## 2. Immediate local retry — 2025 only

Run only:

```powershell
python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2025 `
  --families "portal,talent,ratings" `
  --output local-data/probes/cfbd_native_2025_retry_v1.json

Get-Content "local-data\probes\cfbd_native_2025_retry_v1.json"
```

A 429 remains a transport/rate state, not a data-coverage result. If a 429 recurs, split into individual family runs rather than repeatedly hammering the same endpoint sequence.

Examples:

```powershell
python scripts/probes/cfbd_native_family_probe.py --seasons 2025 --families "portal" --output local-data/probes/cfbd_2025_portal.json
python scripts/probes/cfbd_native_family_probe.py --seasons 2025 --families "talent" --output local-data/probes/cfbd_2025_talent.json
python scripts/probes/cfbd_native_family_probe.py --seasons 2025 --families "ratings" --output local-data/probes/cfbd_2025_ratings.json
```

---

## 3. Talent scope probe after 2025 is known

The row-count evidence strongly suggests a scope/entity-universe change, but row count alone is insufficient.

Target seasons:

```text
2023
2024
2025
```

Required comparison:

```text
CFBD /talent team set
vs
CFBD /teams/fbs?year=<season> team set
```

Measure:

- exact overlap count;
- FBS teams missing from talent;
- talent teams outside the FBS list;
- whether extra teams are FCS/other classifications where resolvable;
- provider ID/name normalization cases.

Do not label the historical talent family FBS-only until this membership comparison is complete.

---

## 4. Player identity case studies

Use bounded examples that stress the canonical identity rules:

### Case A — same-program multi-season player

Verify whether provider athlete ID remains stable across year-to-year roster state changes.

### Case B — single transfer

Trace:

```text
recruiting record
-> player/athlete identity
-> origin roster
-> portal observation
-> destination roster
```

Measure which links are explicit IDs and which require reconciliation.

### Case C — multiple transfers

Confirm one canonical player can own multiple `PLAYER_PROGRAM_STINT` records without identity fragmentation.

### Case D — recruit without athleteId

Demonstrate that a missing recruiting `athleteId` remains unresolved or probabilistically reconciled rather than name-auto-merged.

### Case E — FBS/FCS mover

Test classification-boundary identity continuity.

---

## 5. Coach identity cases

Trace several head coaches across multiple seasons and at least one team change.

Measure:

- provider coach-ID stability;
- nested season semantics;
- team/role change representation;
- interim-head-coach behavior where available.

This does not replace the separate coordinator/play-caller history gap.

---

## 6. Rating-family normalization follow-up

Do not treat Elo/SRS/SP+/FPI/CORE as one generic ratings table.

At minimum preserve:

```text
rating_family
provider_model_version when exposed
through_week / season-type semantics when exposed
entity universe / division
acquired_at
PIT classification
```

Special rules already locked:

- CORE: retrospective public history beginning 2016; PIT-C by default.
- Elo: year-only query defaults to latest available week, so explicit snapshot semantics are required.
- SRS: row universe expands materially from 2022; use row-level division/entity reconciliation.
- FPI: strong FBS-aligned benchmark candidate, but still not automatically PIT-safe.
- SP+: separate provider-derived family with its own provenance and entity reconciliation.

---

## 7. Exit from B.2-B

B.2-B can close when:

1. the 2025 annual gap is resolved or explicitly transport-gated;
2. talent membership scope is directly measured around its observed transition;
3. representative player/transfer identity cases demonstrate the canonical identity rules;
4. representative coach continuity is measured;
5. remaining provider-family gaps are explicit enough for Phase C contracts.

Then proceed to **B.2-C cross-provider reconciliation** rather than performing more broad endpoint discovery.
