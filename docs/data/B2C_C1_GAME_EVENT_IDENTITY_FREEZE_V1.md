# B.2-C C1 — Game / Event Identity Freeze V1

Status: **FROZEN**

Evidence: `PROVIDER_PROBE_RESULTS_V11` through `V14`, culminating in user-executed V4.

## Frozen event candidate rule

Cross-provider event reconciliation begins from explicit provider event IDs when both sources expose them. For the measured completed 2024 CFBD FBS-involved universe, CFBD `game.id` and SportsDataverse/ESPN `game_id` were identical for all 920 events.

Provider IDs remain crosswalk evidence, not canonical Daily-NCAAF identity.

## Frozen participant-orientation rule

Provider home/away sides are observations, not canonical participant identity.

Inside an already exact-ID matched two-participant event:

1. prefer strong two-participant orientation evidence;
2. allow `SAME_SIDE` or `SWAPPED_SIDES` explicitly;
3. if only one participant strongly aligns and the opposite orientation has no competing strong evidence, align the remaining participant by counterpart elimination;
4. if both orientations have competing evidence, retain `AMBIGUOUS`;
5. if evidence is insufficient, retain `UNRESOLVED`.

No global name alias may be manufactured merely to force event reconciliation.

## Frozen score rule

Compare scores only after participant alignment. Raw provider home/away score columns are not comparable before orientation is resolved.

## Frozen event-universe rule

Provider season totals are not compared until event universe is normalized. For the measured 2024 schedules, the ESPN FBS-involved universe was derived from participant-aligned exact matches and contained the same 920 events as CFBD.

Raw ESPN-only FCS/FCS events are broader-universe evidence, not CFBD missingness.

## Frozen temporal rule

Kickoff timestamps remain provider observations with provenance. Cross-provider disagreement does not by itself identify which timestamp means scheduled kickoff, revised kickoff, delayed kickoff or actual start.

## Frozen current-season rule

Current-season comparisons are acquisition snapshots, not final coverage truth. `acquired_at`, source hashes and source-specific lifecycle observations are mandatory.

## Measured 2024 freeze evidence

```text
exact shared event IDs                    920 / 920
normalized FBS overlap                    920 / 920
SAME_SIDE                                 918
SWAPPED_SIDES                               2
counterpart-anchor events                   2
UNRESOLVED                                  0
AMBIGUOUS                                   0
score MATCH                               919
score UNAVAILABLE                           1
score MISMATCH                              0
week MISMATCH                               0
team-ID crosswalk conflicts                 0
participant observations                 1840
unique CFBD team names                    230
unique ESPN team IDs                      230
```

## Change-control rule

This C1 freeze may be revised only by versioning a new freeze document with explicit contradictory evidence or a materially better reconciliation contract. Later phases must not silently redefine these semantics.