# Daily NCAAF — Provider Probe Results V11

**Phase:** B.2-C — Cross-provider reconciliation  
**Status:** C1 initial game/event pass complete; V2 follow-up required  
**Observed local run:** 2026-08-31

---

## 1. Purpose

This document records the first direct CFBD ↔ ESPN/cfbfastR schedule reconciliation run after B.2-B identity work closed.

The initial harness compared:

```text
CFBD /games?year=<season>&seasonType=both&classification=fbs
```

against the public SportsDataverse `espn_cfb_schedules` season asset.

Target seasons:

```text
2024
2026
```

The first pass established a very strong event-ID relationship in 2024 and simultaneously exposed two harness defects that must be corrected before interpreting team-name and 2026 results.

---

## 2. 2024 exact game-ID reconciliation — STRONG POSITIVE EVIDENCE

Observed row counts:

```text
CFBD FBS-involved rows       920
CFBD unique game IDs         920
ESPN/cfbfastR schedule rows  966
ESPN unique game IDs         966
```

Exact game-ID overlap:

```text
exact matches        920
CFBD-only IDs          0
ESPN-only IDs         46
CFBD ID coverage     1.0
```

Locked interpretation:

```text
In the measured 2024 season response,
every CFBD FBS-involved game ID was present as the same ESPN/cfbfastR game_id.
```

This is strong empirical evidence that the measured CFBD game identifier and the SportsDataverse/ESPN `game_id` share the ESPN event-ID namespace for this season.

This is provider crosswalk evidence, not a reason to make an external provider ID the canonical Daily-NCAAF game identity.

---

## 3. Raw ESPN-only events are primarily broader-universe events

The initial 46 ESPN-only examples include many obvious FCS/FCS events involving programs such as:

```text
Delaware
Bryant
North Carolina A&T
Pennsylvania
Towson
North Dakota State
Sacramento State
Northern Arizona
Montana State
Missouri State
```

The first schedule asset did not expose populated division/classification columns, so V1 correctly left the raw extra set as:

```text
UNIVERSE_DIFFERENCE_UNTIL_NORMALIZED
```

Do not classify these 46 rows as CFBD omissions.

V2 will normalize the ESPN universe by deriving ESPN FBS team IDs from exact matched-game sides where CFBD provides the FBS/FCS classification, then applying those team IDs to the full ESPN schedule.

---

## 4. Week agreement — COMPLETE IN MEASURED 2024 MATCH SET

Observed:

```text
week MATCH 920 / 920
```

This is strong evidence that the providers agree on the week number for all exact-ID matched 2024 CFBD FBS-involved events in this acquisition.

---

## 5. Kickoff agreement — HIGH BUT NOT PERFECT

Observed:

```text
kickoff MATCH      905 / 920
kickoff MISMATCH    15 / 920
```

The V1 harness treated differences greater than 60 seconds as mismatches.

The generic mismatch-example list was dominated by team display-name differences and therefore did not surface these 15 kickoff cases directly.

V2 must emit field-specific kickoff mismatch examples including exact delta seconds before the discrepancies are interpreted.

Potential explanations include schedule revisions, provider refresh timing, historical schedule corrections, or true source disagreement. No explanation is locked until the exact 15 cases are inspected.

---

## 6. Score agreement — VERY HIGH, WITH TWO REAL CASES TO INSPECT

Observed:

```text
score MATCH        917 / 920
score MISMATCH       2 / 920
score UNAVAILABLE    1 / 920
```

Again, V1's generic mismatch examples were consumed by team display-name differences.

V2 must surface the exact two score mismatches and the one unavailable case before assigning semantics.

No score-disagreement explanation is currently locked.

---

## 7. Team-name comparison in V1 was not a valid identity test

V1 reported:

```text
home_team_state MISMATCH 920
away_team_state MISMATCH 920
```

Inspection shows the dominant reason is presentation naming:

```text
CFBD: Alabama
ESPN: Alabama Crimson Tide

CFBD: Western Kentucky
ESPN: Western Kentucky Hilltoppers

CFBD: Georgia
ESPN: Georgia Bulldogs
```

Therefore these counts are not evidence of team-identity disagreement.

Locked rule:

```text
provider display-name equality != team identity test
```

V2 derives a provider team crosswalk from same-side participation inside exact matched game IDs:

```text
CFBD team name -> ESPN team_id + ESPN display name
```

and reports conflict counts if one CFBD team name maps to multiple ESPN team IDs or vice versa.

Display-name text remains diagnostic only.

---

## 8. Lifecycle comparison in V1 was under-parsed

The ESPN schedule asset exposed a `status` column but not a `completed` column.

V1 only attempted boolean-style completed fields, producing:

```text
lifecycle UNAVAILABLE 920 / 920
```

This is a harness limitation, not provider evidence.

V2 parses coarse ESPN status states such as final/scheduled/canceled into a completed-state observation where defensible while retaining the raw status string.

This should allow direct inspection of the known 2024 Liberty-at-App-State cancellation case.

---

## 9. 2026 V1 failure was an asset-selection bug, not missing SportsDataverse coverage

V1 fabricated this source URL:

```text
cfb_schedule_2026.csv.gz
```

and received HTTP 404.

The current `espn_cfb_schedules` release manifest instead publishes 2026 as, among other formats:

```text
cfb_schedule_2026.csv
cfb_schedule_2026.parquet
cfb_schedule_2026.rds
```

There is no `cfb_schedule_2026.csv.gz` asset in the observed release manifest.

Therefore:

```text
V1 HTTP 404 != missing 2026 schedule dataset
```

V2 resolves the season asset from the release manifest and prefers:

```text
.csv.gz
.csv
```

in that order, avoiding a pyarrow/pandas dependency for this research harness.

---

## 10. Source evidence from the first 2024 run

The first 2024 asset acquisition recorded:

```text
source:
https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_schedules/cfb_schedule_2024.csv.gz

byte_count: 33299
sha256: 4fb9c661e76a9ecc3748878a7e5d6a3aa9cb9b6c82140e44a1812151e6e16645
```

The hash matches the currently advertised release digest for that asset.

This evidence must remain immutable in the audit record even if SportsDataverse later refreshes the release.

---

## 11. C1 status after the first run

### Strongly supported

- exact CFBD ↔ ESPN game-ID equality is extremely strong in measured 2024 FBS-involved events;
- no CFBD-only 2024 game IDs were observed;
- week agreement was 100% for matched events;
- raw ESPN schedule universe is broader than the CFBD FBS-involved query universe;
- source assets need immutable hash/acquisition evidence.

### Requires V2 rerun

- normalize ESPN-only events using side-derived ESPN FBS team IDs;
- derive CFBD-team ↔ ESPN-team-ID crosswalk and check conflicts;
- inspect all 15 kickoff mismatches;
- inspect both score mismatches and the unavailable score case;
- parse ESPN `status` for lifecycle comparison;
- rerun 2026 using the actual manifest-selected asset.

---

## 12. Next gate

Run:

```text
cross_provider_game_reconciliation_probe_v2.py
```

for:

```text
2024
2026
```

If exact event IDs remain clean after universe normalization and team crosswalk conflicts are absent or explainable, C1 can close and B.2-C can move to program/team-ID reconciliation followed by player-level cross-provider reconciliation.
