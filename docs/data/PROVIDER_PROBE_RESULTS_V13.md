# Daily NCAAF — Provider Probe Results V13

## Scope

This evidence record captures the successful B.2-C C1 V3 run on 2026-09-01 and the final instrumentation issue it exposed before C1 game/event identity can be frozen.

Source output:

```text
local-data/probes/cross_provider_games_v3.json
contract: DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V3
generated_at: 2026-09-01T07:27:13.859909+00:00
```

Research-only probe. Provider secrets remain environment-only and are not emitted.

---

# P-050 — 2024 exact event-ID reconciliation is complete at the normalized FBS universe level

Measured 2024 state:

```text
CFBD FBS-involved rows                  920
CFBD unique game IDs                    920
SportsDataverse/ESPN rows               966
SportsDataverse unique game IDs         966
exact shared game IDs                   920
CFBD-only raw IDs                         0
ESPN-only raw IDs                        46
normalized ESPN FBS-involved events     920
normalized overlap with CFBD             920
normalized CFBD-only                       0
normalized ESPN-only                       0
```

The 46 raw ESPN-only events are outside the CFBD `classification=fbs` event universe and disappear after participant-aligned FBS normalization.

Locked conclusion:

```text
provider season totals are not comparable until event universe is normalized
```

For the measured 2024 FBS-involved universe, CFBD `id` and SportsDataverse/ESPN `game_id` empirically share the same event-ID namespace.

---

# P-051 — Provider home/away orientation is not event identity

V3 correctly resolved the two V2 bowl side swaps:

```text
401677085  CFBD UTSA home / Coastal Carolina away
           ESPN Coastal Carolina home / UTSA away

401677093  CFBD USC home / Texas A&M away
           ESPN Texas A&M home / USC away
```

V3 state:

```text
SAME_SIDE       916
SWAPPED_SIDES     2
UNRESOLVED        2
```

Both swapped events produced team-aligned score matches and no crosswalk conflicts.

Locked:

```text
same exact event + same participant set + swapped provider sides != identity conflict
provider home/away side != canonical participant identity
```

---

# P-052 — The remaining two unresolved orientations are a display-alias instrumentation edge case

Only two 2024 exact-ID matched events remained unresolved:

```text
401644732  Kent State vs Saint Francis
401644737  Eastern Michigan vs Saint Francis
```

SportsDataverse/ESPN displays the opponent as:

```text
St. Francis (PA) Red Flash
```

while CFBD displays:

```text
Saint Francis
```

In both events the other participant is independently and strongly aligned on the same side:

```text
Kent State -> ESPN Kent State Golden Flashes
Eastern Michigan -> ESPN Eastern Michigan Eagles
```

Because exact event-ID equality already establishes the two-participant event candidate, the independently aligned participant can conservatively anchor the remaining participant by elimination when the opposite orientation has no competing strong identity evidence.

This is not a global name alias rule.

New general rule:

```text
EXACT EVENT ID
+ exactly two provider participants
+ one strong participant alignment
+ zero competing opposite-orientation anchors
=> remaining participant may be aligned by counterpart elimination
```

The evidence basis must remain explicit and auditable.

V4 adds:

```text
participant_alignment_basis =
    TWO_PARTICIPANT_DISPLAY_EVIDENCE
    ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR
    COMPETING_TWO_PARTICIPANT_DISPLAY_EVIDENCE
    COMPETING_ONE_PARTICIPANT_ANCHORS
    INSUFFICIENT_PARTICIPANT_DISPLAY_EVIDENCE
```

---

# P-053 — Team crosswalk evidence is conflict-free after participant alignment

V3 2024 crosswalk:

```text
participant observations                         1836
unique CFBD team names                             229
unique ESPN team IDs                               229
CFBD name -> multiple ESPN ID conflicts              0
ESPN ID -> multiple CFBD name conflicts              0
matched games skipped for unresolved orientation     2
```

The two skipped games are exactly the Saint Francis alias cases above.

Expected V4 terminal candidate if counterpart anchoring behaves as designed:

```text
participant observations                         1840
matched games skipped                               0
unique CFBD team names                             230
unique ESPN team IDs                               230
CFBD name -> multiple ESPN ID conflicts              0
ESPN ID -> multiple CFBD name conflicts              0
```

Expected new crosswalk evidence:

```text
CFBD Saint Francis -> ESPN team ID 2598 / St. Francis (PA) Red Flash
```

This remains provider crosswalk evidence, not canonical Daily-NCAAF identity.

---

# P-054 — 2024 score/lifecycle agreement after side correction

V3:

```text
score MATCH                    917
score UNAVAILABLE                1
score UNRESOLVED_ORIENTATION     2
score MISMATCH                   0
lifecycle MATCH                920
week MATCH                     920
```

The one unavailable score corresponds to the canceled Liberty-at-App-State event.

If V4 resolves the two alias cases, expected score state is:

```text
MATCH       919
UNAVAILABLE   1
MISMATCH      0
```

No score discrepancy currently remains unexplained after participant alignment.

---

# P-055 — Kickoff values are source-time observations, not a single proven semantic

2024 V3 kickoff buckets:

```text
<= 60 seconds             905
> 60 sec <= 5 min           1
> 5 min <= 30 min            6
> 30 min <= 2 hours          6
> 2 hours                     2
```

Examples span small five-/ten-/nineteen-minute shifts through large multi-hour differences.

Locked:

```text
provider kickoff field != silently assumed canonical scheduled kickoff
```

Future canonical time semantics must distinguish, where evidence permits:

```text
scheduled kickoff
revised kickoff
actual start
weather/delay start
unknown source-time semantic
```

Historical disagreement alone does not prove which provider is correct.

---

# P-056 — 2026 confirms acquisition-state and update-cadence differences

At V3 acquisition:

```text
CFBD 2026 events                    888
SportsDataverse/ESPN events           8
exact shared IDs                      8
SportsDataverse-only                  0
CFBD-only                            880
```

All eight shared events had matching kickoff times and same-side participant orientation.

Three shared events were already final in CFBD while the immutable downloaded SportsDataverse artifact still contained `STATUS_IN_PROGRESS` with intermediate scores:

```text
401858201  Stanford / Hawai'i
401864570  Florida State / New Mexico State
401866408  Eastern Michigan / Sacramento State
```

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

This is useful B.2-D evidence but does not replace prospective repeated live capture.

---

# P-057 — Freshest supported manifest asset selection is validated

V3 selected the newer plain CSV assets rather than older gzip assets.

2024:

```text
asset cfb_schedule_2024.csv
created/updated 2026-09-01T03:26:59Z
SHA-256 6249cc0922e3fe3eade3634b733bd193b92b5b07e6ee4ca456b5efd2b670ca86
advertised digest match = true
```

2026:

```text
asset cfb_schedule_2026.csv
updated 2026-09-01T06:33:58Z
SHA-256 d458d6a80fb037718001320f3e5dbc9d126c72db4c8bc14c47df9f9d8bb55c8e
advertised digest match = true
```

Locked source-selection rule:

```text
freshness outranks format preference
format breaks timestamp ties only
```

Downloaded artifact hash and acquisition timestamp remain part of evidence provenance.

---

# C1 status after V3

```text
C1 GAME / EVENT IDENTITY = FINAL EXIT CANDIDATE, NOT YET FROZEN
```

Only remaining reproducible gate:

1. run V4 counterpart-anchor tests;
2. run V4 for 2024/2026;
3. require zero unexplained 2024 orientations;
4. require zero team crosswalk conflicts;
5. require normalized 2024 FBS overlap to remain 920/920;
6. require the two Saint Francis cases to resolve through explicit counterpart-anchor evidence rather than a hard-coded alias.

If those pass, freeze C1 and advance to C2 program/team crosswalk contract and C3 player cross-provider reconciliation.
