# Provider Probe Results V19 — B.2-C C5-A Context Reconciliation

Date: 2026-09-03
Status: **C5-A MEASURED / PARTIAL — SOURCE-SHAPE LIMITED**

## Scope

User-executed probe:

```text
scripts/probes/cross_provider_context_reconciliation_probe.py
contract: DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V1
seasons: 2023, 2024, 2025
```

Offline suite:

```text
11 tests
OK
```

The audit compares the CFBD `/games` delivery path against the ESPN-native `espn_cfb_schedules` release only after exact game identity and C1 participant orientation are established.

Per `B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md`, this is delivery-path compatibility evidence inside an ESPN-origin ecosystem, not independent-source corroboration.

## Exact-event coverage

```text
season  CFBD rows  ESPN-native rows  exact shared IDs  CFBD exact-ID coverage
2023       910          911                 910                100%
2024       920          966                 920                100%
2025       934          958                 934                100%
```

No CFBD-only exact event IDs occurred in the measured completed-season window.

## Critical source-shape finding

The selected ESPN-native schedule CSVs contained:

```text
game_id
season
week
season_type
game_date
neutral_site
conference_competition
home_id
away_id
home_team
away_team
home_abbreviation
away_abbreviation
home_score
away_score
home_winner
away_winner
venue
attendance
status
```

They did **not** contain:

```text
venue_id
home_conference
away_conference
home_division
away_division
```

Therefore the V1 probe correctly reported these fields as `UNAVAILABLE` for every matched game:

```text
venue_id_state
home_conference_state
away_conference_state
home_division_state
away_division_state
```

Locked:

```text
field absent from selected source artifact != disagreement
UNAVAILABLE != MISMATCH
source-shape limitation != provider identity failure
```

C5 cannot freeze the venue-ID / affiliation / classification portions from `espn_cfb_schedules` alone.

## Usable C5-A evidence

### Participant orientation

```text
2023  SAME_SIDE 906  SWAPPED_SIDES 4
2024  SAME_SIDE 918  SWAPPED_SIDES 2
2025  SAME_SIDE 934  SWAPPED_SIDES 0
```

No unresolved or ambiguous orientation examples occurred.

### Venue display text

```text
season  EXACT  MISMATCH
2023     815      95
2024     830      90
2025     827     107
```

Examples show sponsor/branding/history drift such as:

```text
FIU Stadium <-> Riccardo Silva Stadium
Memorial Stadium (Champaign, IL) <-> Gies Memorial Stadium
Razorback Stadium <-> Donald W. Reynolds Razorback Stadium
Ryan Field <-> Ryan Field (1926)
Gesa Field <-> Martin Stadium
FBC Mortgage Stadium <-> Acrisure Bounce House
```

A venue display-name mismatch is therefore not sufficient evidence of a venue identity break.

Locked:

```text
venue display text != venue identity
venue rename/sponsor drift != new canonical VENUE
```

### Neutral-site observation

```text
season  MATCH  MISMATCH
2023     907       3
2024     901      19
2025     925       9
```

Mismatch examples include repeat clusters involving alternate/temporary home settings and special-site events. Examples include Northwestern games at Martin Stadium/Wrigley Field, Kansas games at Kansas City venues, FIU/Sam Houston alternate-site observations, and selected postseason/special-site events.

C5-A does **not** choose one flag as truth.

Locked:

```text
CFBD neutralSite != automatically canonical neutral-site truth
ESPN-native neutral_site != automatically canonical neutral-site truth
neutral-site disagreement remains provider/context evidence
```

### Conference-game flag semantics

```text
season  MATCH  MISMATCH
2023     898      12
2024     909      11
2025     933       1
```

The mismatch examples are concentrated in special semantic contexts, including conference championship games and independent/Army-Navy style cases.

Examples include:

```text
2023 Washington-Oregon Pac-12 championship
2023 Texas-Oklahoma State Big 12 championship
2023 Alabama-Georgia SEC championship
2024 SMU-Clemson ACC championship
2024 Oregon-Penn State Big Ten championship
2024 Texas-Georgia SEC championship
2024 Army-Navy
2025 Army-Navy
```

This confirms the prior contract decision that the two flags must not be collapsed into one canonical boolean without semantic reconciliation.

Locked:

```text
CFBD conferenceGame != ESPN conference_competition semantics by definition
conference-game flag != conference affiliation proof
flag mismatch != program identity failure
```

## Source evidence

All selected ESPN-native schedule assets returned HTTP 200 and matched their advertised SHA-256 digests.

```text
2023 cfb_schedule_2023.csv
sha256 5739569b8e7684ed6fa838c9e3cf13ab1d62f223cef0e7785e466544d5d0a7c1

2024 cfb_schedule_2024.csv
sha256 6249cc0922e3fe3eade3634b733bd193b92b5b07e6ee4ca456b5efd2b670ca86

2025 cfb_schedule_2025.csv
sha256 2b8e4e24f3c62c8833b7e15703675d9648f438aaa01de966e6498eae50b1d86f
```

Manifest acquired during the user run:

```text
release tag: espn_cfb_schedules
release updated_at: 2026-09-02T14:58:54Z
asset_count: 95
```

## C5-A conclusion

C5-A successfully measured the fields the native schedule artifact actually exposes and, equally importantly, proved which requested comparisons that artifact **cannot** support.

C5 remains active.

The next bounded pass is C5-B:

1. use the ESPN-native team-season metadata compiled in `espn_cfb_teams` for `division`, `conference_*`, and home `venue_id`;
2. compare participant classification and conference only through exact external team IDs already frozen in C2;
3. use ESPN home-venue metadata only as a conservative standard-home-venue crosswalk anchor, not as direct event-venue truth;
4. retain the C5-A neutral-site and conference-game flag disagreements as separate provider observations;
5. do not use backported CFBD columns from the mixed `espn_cfb_teams` release as ESPN evidence.
