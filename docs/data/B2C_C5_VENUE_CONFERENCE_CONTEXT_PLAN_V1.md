# B.2-C C5 — Venue / Conference / Context Reconciliation Plan V1

Status: **ACTIVE — C5-A MEASURED/PARTIAL; C5-B ACTIVE**
Date: 2026-09-03

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3 player cross-provider identity — COMPLETE/FROZEN
- C4 transfer-event reconciliation — COMPLETE/FROZEN
- `B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md` governs evidentiary wording

## Objective

Measure event and team-season context compatibility across the CFBD API delivery path and ESPN-native SportsDataverse artifacts after exact event identity and participant orientation are already established.

C5 is a **delivery-path reconciliation audit**, not independent-source truth confirmation.

## Completed-season window

```text
2023
2024
2025
```

This window spans major conference realignment, neutral/postseason events and recent FBS membership transitions while avoiding current-season snapshot incompleteness.

# C5-A — ESPN-native schedule context — MEASURED / PARTIAL

Tooling:

```text
scripts/probes/cross_provider_context_reconciliation_probe.py
tests/probes/test_cross_provider_context_reconciliation_probe.py
```

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V19.md
```

User-executed suite:

```text
11 tests
OK
```

Exact event coverage:

```text
2023  910 / 910 CFBD games matched
2024  920 / 920 CFBD games matched
2025  934 / 934 CFBD games matched
```

## C5-A source-shape finding

The selected `espn_cfb_schedules` CSVs expose game-level fields including:

```text
game_id
neutral_site
conference_competition
home_id
away_id
home_team
away_team
venue
```

but they do **not** expose:

```text
venue_id
home_conference
away_conference
home_division
away_division
```

Therefore those comparisons were correctly `UNAVAILABLE` rather than mismatches.

Locked:

```text
field absent from source artifact != disagreement
UNAVAILABLE != MISMATCH
source-shape limitation != provider identity failure
```

## C5-A measured fields

Venue display text:

```text
2023  EXACT 815  MISMATCH 95
2024  EXACT 830  MISMATCH 90
2025  EXACT 827  MISMATCH 107
```

Examples demonstrate sponsor/branding/history drift. Venue display text is not venue identity.

Neutral-site flags:

```text
2023  MATCH 907  MISMATCH 3
2024  MATCH 901  MISMATCH 19
2025  MATCH 925  MISMATCH 9
```

The mismatches remain provider/context observations. Neither flag becomes canonical truth by default.

Conference-game flags:

```text
2023  MATCH 898  MISMATCH 12
2024  MATCH 909  MISMATCH 11
2025  MATCH 933  MISMATCH 1
```

Mismatch examples concentrate in special semantic contexts such as conference championships and independent/Army-Navy cases. `conferenceGame` and `conference_competition` must remain distinct raw observations.

# C5-B — Team-season context / home-venue anchor — ACTIVE

Plan:

```text
docs/data/B2C_C5_CONTEXT_FOLLOWUP_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v2.py
tests/probes/test_cross_provider_context_reconciliation_probe_v2.py
```

## C5-B input

SportsDataverse `espn_cfb_teams` publishes season-level team metadata with documented ESPN-native fields including:

```text
team_id
division
is_fbs
conference_id
conference_name
conference_short_name
conference_abbreviation
conference_midsize_name
venue_id
venue_name
```

The published table also contains explicitly backported CFBD-only fields. C5-B must whitelist only the ESPN-native fields and must never use `cfbd_conference`, `classification`, or other backported CFBD columns as second-path evidence.

## Participant classification

After exact event match and C1 orientation:

```text
CFBD homeClassification / awayClassification
vs
ESPN team-season division
```

Classification is a program-season/context state, not program identity.

## Participant conference

After exact team-ID resolution:

```text
CFBD homeConference / awayConference
vs
ESPN-native conference alias set
```

Alias fields:

```text
conference_name
conference_short_name
conference_abbreviation
conference_midsize_name
```

Missing ESPN conference metadata remains unavailable rather than being fabricated.

## Venue identity / home-venue anchor

C5-A could not directly compare event venue IDs because the native schedule artifact does not expose one.

C5-B therefore uses ESPN team-season `venue_id` only as a **home-venue observation**. It may be compared to CFBD event `venueId` only under conservative standard-home context:

```text
orientation == SAME_SIDE
CFBD neutralSite == false
ESPN neutral_site == false
same external home team ID
both venue IDs available
```

States:

```text
MATCH
DIFFERENT_FROM_TEAM_HOME_VENUE
UNAVAILABLE
NOT_APPLICABLE_CONTEXT
```

A difference may represent an alternate designated home site and is not an automatic venue identity failure.

Locked distinction:

```text
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
team-season home venue != event venue by definition
```

# Production concepts being tested

```text
VENUE
VENUE_PROVIDER_CROSSWALK
HOME_VENUE_STINT
GAME_VENUE_OBSERVATION
GAME_CONTEXT_OBSERVATION
CONFERENCE_AFFILIATION_STINT
CLASSIFICATION_STINT
```

The production schema must preserve raw event/context observations before deriving canonical context.

# Safety rules

```text
provider venue ID != canonical VENUE_ID
venue display-name change != venue identity break
conference label != PROGRAM identity
conference change != new PROGRAM
classification change != new PROGRAM
neutral-site flag != home/away identity authority
conferenceGame flag != conference affiliation proof
team home venue != direct event venue proof
CFBD-backported team columns != ESPN-native evidence
shared upstream origin != independent corroboration
cross-delivery agreement != PIT safety
```

# C5 freeze candidate criteria

C5 may freeze after C5-B when:

1. C5-A source-shape limitations remain explicit;
2. exact matched events provide enough usable context evidence across 2023-2025;
3. participant-side comparison always uses C1 orientation semantics;
4. classification/conference disagreements and unavailable states are quantified and never silently normalized away;
5. standard-home venue-ID anchors demonstrate either a stable external namespace or bounded alternate-site exceptions without substituting home venue for event venue;
6. neutral-site disagreements are explicit;
7. conference-game flag disagreements remain a separate semantic class rather than affiliation failures;
8. mixed ESPN/CFBD provenance in the team table is field-level separated;
9. canonical venue/conference/classification identities remain provider-independent.
