# B.2-C C5-B — Team-Season Context / Home-Venue Anchor Follow-Up V1

Date: 2026-09-03
Status: **ACTIVE**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C5-A native schedule context pass — MEASURED/PARTIAL
- `PROVIDER_PROBE_RESULTS_V19.md`
- `B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md`

## Why C5-B exists

C5-A proved that the selected `espn_cfb_schedules` CSVs do not expose event `venue_id` or participant conference/division fields. Those fields therefore cannot be evaluated from that artifact and must not be inferred from nulls.

SportsDataverse now also publishes an `espn_cfb_teams` season dataset. Its compiler documents ESPN-native fields including:

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

The published `espn_cfb_teams` table also carries explicitly backported CFBD-only fields. **C5-B must never use those backported fields as ESPN evidence.**

Forbidden evidence columns include, at minimum:

```text
cfbd_conference
classification
school
mascot
city
state
country_code
timezone
latitude
longitude
elevation
capacity
dome
grass
```

The C5-B report must record that provenance boundary explicitly.

## Objectives

C5-B answers four bounded questions.

### 1. Participant division/classification agreement

For every exact-ID matched event and each participant after C1 orientation:

```text
CFBD game participant external team ID
      ==
ESPN schedule aligned team ID
      ==
ESPN team-season metadata team_id
```

Then compare:

```text
CFBD homeClassification / awayClassification
vs
ESPN-native team-season division
```

States:

```text
MATCH
MISMATCH
UNAVAILABLE_TEAM_METADATA
UNRESOLVED_ORIENTATION
```

### 2. Participant conference agreement

Compare each CFBD game conference label against the set of ESPN-native conference aliases for the same team-season:

```text
conference_name
conference_short_name
conference_abbreviation
conference_midsize_name
```

Do not compare to `cfbd_conference`.

States:

```text
EXACT_ALIAS_MATCH
NORMALIZED_ALIAS_MATCH
MISMATCH
UNAVAILABLE_TEAM_METADATA
UNAVAILABLE_ESPN_CONFERENCE
UNRESOLVED_ORIENTATION
```

A team with no ESPN conference must remain unavailable rather than being forced into an invented independent conference identity.

### 3. Standard-home-venue external ID anchor

The ESPN team-season `venue_id` is the team's **home venue**, not the event venue.

Therefore it may only be used as a conservative anchor when all of the following hold:

```text
C1 orientation == SAME_SIDE
CFBD neutralSite == false
ESPN-native schedule neutral_site == false
CFBD home participant ID == ESPN schedule home participant ID
ESPN team-season home venue_id is available
CFBD event venueId is available
```

Then compare:

```text
CFBD event venueId
vs
ESPN team-season home venue_id
```

States:

```text
MATCH
DIFFERENT_FROM_TEAM_HOME_VENUE
UNAVAILABLE
NOT_APPLICABLE_CONTEXT
```

A difference does **not** mean either venue ID is wrong. It may represent an alternate designated home site.

C5-B may establish that shared numeric venue IDs are strong external crosswalk evidence for standard home venues. It may **not** claim that the team-season home venue ID is the direct event venue ID for every game.

### 4. Preserve C5-A event-only semantics

C5-B does not replace the native schedule observations:

```text
neutral_site
conference_competition
venue display text
```

Those remain separate game-context observations with the C5-A disagreement counts.

## Season window

```text
2023
2024
2025
```

## Required source evidence

For each `espn_cfb_teams` season asset record:

```text
release tag
release updated_at
asset name
asset updated_at
source URL
byte count
SHA-256
advertised digest
advertised digest match
columns
acquired_at
```

Only plain/gzip CSV assets are required by this standard-library audit harness.

## Team metadata integrity checks

Per season:

```text
row count
non-null team IDs
unique team IDs
duplicate team-ID rows
FBS team count
```

For every external team ID referenced by a matched FBS-involved game, C5-B must classify whether team-season metadata is present.

Missing metadata must remain explicit.

## Production concepts being tested

```text
PROGRAM_SEASON
CONFERENCE_AFFILIATION_STINT
CLASSIFICATION_STINT
VENUE
VENUE_PROVIDER_CROSSWALK
HOME_VENUE_STINT
GAME_VENUE_OBSERVATION
GAME_CONTEXT_OBSERVATION
```

Important separation:

```text
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
conference affiliation != conference-game flag
classification state != program identity
```

## Safety rules

```text
team-season ESPN venue_id != direct event venue proof
provider venue ID != canonical VENUE_ID
conference alias match != canonical conference identity by itself
conference label mismatch != new PROGRAM
classification mismatch != new PROGRAM
missing ESPN team metadata != nonexistence
CFBD-backported team columns != ESPN-native evidence
shared upstream origin != independent corroboration
cross-delivery agreement != PIT safety
```

## C5 freeze criteria after C5-B

C5 may freeze after C5-B if:

1. the C5-A source-shape limitation remains explicit;
2. participant division/classification reconciliation is complete enough to establish safe production missingness/mismatch states;
3. participant conference reconciliation is complete enough to establish safe alias and unavailable semantics;
4. standard-home-venue anchors either demonstrate a stable shared external venue-ID namespace or expose bounded exceptions without forcing event-venue identity;
5. neutral-site and conference-game flag disagreements remain separate provider observations;
6. no team home venue is substituted for an event venue when context says that is unsafe;
7. mixed-source columns in `espn_cfb_teams` are provenance-separated;
8. canonical program/conference/venue identities remain provider-independent.
