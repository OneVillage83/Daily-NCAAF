# Daily NCAAF — Provider Probe Results V10

**Phase:** B.2-B — CFBD Targeted Identity Hard Cases  
**Status:** COMPLETE; B.2-B EXIT GATE SATISFIED  
**Probe generated:** 2026-08-31T21:55:22Z  
**Harness contract:** `DAILY_NCAAF_PHASE_B2_CFBD_RECRUIT_LINKAGE_GAP_PROBE_V1`

---

## 1. Purpose

This document records the final B.2-B hard-case audit for recruiting rows where `athleteId` is null.

The probe asked:

```text
recruit.athleteId = null
-> can roster.recruitIds recover a direct provider link?
```

It also measured normalized-name collisions to test whether names can safely repair missing provider links.

Local test result before execution:

```text
Ran 9 tests in 0.003s
OK
```

All requested provider calls in the run returned HTTP 200.

---

## P-054 — Missing recruiting athleteId is common even among FBS-committed records

Observed recruiting rows:

| Year | Recruit rows | athleteId null | FBS-committed + athleteId null |
|---:|---:|---:|---:|
| 2021 | 3,364 | 1,115 | 437 |
| 2022 | 3,955 | 1,232 | 240 |
| 2023 | 4,166 | 1,503 | 240 |
| 2024 | 4,236 | 1,580 | 291 |

Therefore missing direct recruiting-to-athlete linkage is not an edge case.

Locked consequence:

```text
recruit.athleteId = null
!= no eventual college athlete
!= safe name merge
```

---

## P-055 — Sampled roster recruitIds did not recover the tested recruiting record IDs

The probe selected three deterministic high-ranked FBS-committed `athleteId = null` recruiting rows per year for 2021-2024.

Across all 12 selected cases:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK                 0
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE     8
UNRESOLVED                                    4
```

No sampled roster row contained the tested recruiting-record ID in its `recruitIds` list.

Examples:

```text
2021 Marques Buford Jr.
recruit row id: 254930
stable roster athlete id: 4686045
roster recruitIds: [190078]

2022 Samuel Dankah
recruit row id: 255783
stable roster athlete id: 4906210
roster recruitIds: [190071]

2023 Zachariah Branch
recruit row id: 111251
stable roster athlete id: 4870612
roster recruitIds: [113601]
```

The safe conclusion is **not** that roster `recruitIds` can never be useful. The measured conclusion is:

```text
roster.recruitIds cannot be assumed to use the same directly joinable record identity
as the recruiting row selected from /recruiting/players
```

until its semantics are independently proven for the relevant record/era.

A numerically different `recruitIds` value must not be silently remapped to the tested recruiting record by name.

---

## P-056 — Stable same-name roster candidates remain contextual evidence only

Eight selected cases produced one stable same-name roster athlete candidate across the bounded roster window without a direct recruiting-record-ID match.

Examples include:

```text
Marques Buford Jr. -> roster athlete 4686045
Lorenz Terry       -> roster athlete 4710660
Samuel Dankah      -> roster athlete 4906210
Oumar Conde        -> roster athlete 4912914
TJ Urban           -> roster athlete 5082632
Zachariah Branch   -> roster athlete 4870612
Caleb Herring      -> roster athlete 4870738
Jayvon Thomas      -> roster athlete 4871075
```

These are useful reconciliation candidates but remain:

```text
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
```

not direct provider links.

Future reconciliation may raise some to `HIGH_CONFIDENCE_RECONCILED` only by combining independent evidence such as school/program chronology, position, physical/hometown data, recruiting metadata, cross-provider IDs, and other stable attributes.

Name agreement by itself is insufficient.

---

## P-057 — Some FBS commitment records remain unresolved in the bounded roster window

Four sampled cases produced no exact-name roster candidate in the committed program for the queried season/following-season window:

```text
2021 Quinn Ewers        -> Ohio State -> UNRESOLVED
2024 Gatlin Bair        -> Oregon     -> UNRESOLVED
2024 Jamroc Grimsley    -> Alabama    -> UNRESOLVED
2024 Demond Williams Jr.-> Arizona    -> UNRESOLVED
```

The probe does not assign a causal explanation to these absences.

Possible real-world/provider mechanisms can include commitment changes, delayed enrollment, transfer/reclassification timing, provider revision semantics, or roster coverage differences.

Locked consequence:

```text
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
```

A commitment is recruiting-state evidence. Actual program membership must be supported by roster/enrollment/participation or other reconciled evidence.

---

## P-058 — Normalized-name collisions empirically prove name-only identity is unsafe

Every tested year produced multiple recruiting records sharing the same normalized name.

Examples include:

```text
2021 Andrew Jones
  Memphis LB, athleteId null
  Duke OT, athleteId 4601280

2021 Austin Smith
  Eastern Michigan QB, athleteId 4917292
  Colorado TE, athleteId 4685559

2022 AJ Barton
  UTEP OT, recruit id 255925, athleteId null
  UTEP OT, recruit id 255926, athleteId null

2022 DJ Moore / D.J. Moore
  Indiana IOL, athleteId 5081326
  Georgia Tech WR, athleteId 4840124

2023 Daniel Harris
  Georgia CB, athleteId 4870753
  UAB EDGE, athleteId 4870751

2024 Ashton Hampton
  Clemson S, athleteId 5127738
  Texas Tech S, athleteId 5149496
```

The AJ Barton example is especially important: normalized name, committed program, and position can all coincide while two provider recruiting records remain distinct.

Therefore even composite rules such as:

```text
name + school
name + school + position
```

cannot be treated as universally unique identity keys.

Locked rule:

```text
NAME MATCH != IDENTITY MATCH
```

---

## P-059 — Missing-link reconciliation must preserve explicit confidence state

The measured evidence supports the planned reconciliation-state contract:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

Provider-specific intermediate observations may additionally record:

```text
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
```

but this is not a canonical identity assignment.

A production resolver must preserve:

- candidate evidence;
- evidence provenance;
- competing candidates;
- decision reason;
- confidence/threshold version;
- rejection/ambiguity state;
- manual-review status where applicable.

No resolver may silently force every source row onto a canonical player.

---

## B.2-B final verdict — COMPLETE

B.2-B now has empirical evidence for both the clean and failure paths.

Verified clean paths:

1. stable roster athlete IDs across same-program seasons;
2. stable roster athlete IDs through multiple FBS transfers;
3. stable roster athlete IDs through FCS -> FBS movement;
4. direct recruiting `athleteId` -> roster athlete-ID linkage when exposed;
5. stable coach IDs through school changes.

Verified hard/failure paths:

1. recruiting `athleteId` is materially incomplete;
2. sampled roster `recruitIds` did not directly recover the tested recruiting record IDs;
3. stable same-name roster candidates can exist without a direct provider link;
4. commitment records can remain unresolved against the bounded committed-program roster window;
5. same normalized name can map to multiple distinct recruiting records and athlete IDs;
6. name + school + position is not guaranteed unique;
7. portal observations lack an explicit player identifier in the measured rows;
8. provider fields cannot be assumed to define canonical temporal/entity semantics.

No new failure mode requires additional broad CFBD-only discovery before cross-provider reconciliation.

Therefore:

```text
B.2-B — COMPLETE
B.2-C — ACTIVE NEXT
```

The next phase is CFBD <-> ESPN/cfbfastR reconciliation, beginning with exact game-ID/event-universe measurement before player and transfer crosswalk work.