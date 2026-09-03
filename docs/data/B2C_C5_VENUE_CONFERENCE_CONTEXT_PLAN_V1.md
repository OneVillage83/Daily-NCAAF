# B.2-C C5 — Venue / Conference / Context Reconciliation Plan V1

Status: **ACTIVE**
Date: 2026-09-03

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3 player cross-provider identity — COMPLETE/FROZEN
- C4 transfer-event reconciliation — COMPLETE/FROZEN
- `B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md` governs evidentiary wording

## Objective

Measure whether event context fields agree between the CFBD API delivery path and the ESPN-native SportsDataverse schedule artifact after exact event identity and participant orientation are already established.

C5 is a **delivery-path reconciliation audit**, not independent-source truth confirmation.

## Completed-season window

```text
2023
2024
2025
```

This window spans major conference realignment, neutral/postseason events and recent FBS membership transitions while avoiding current-season snapshot incompleteness.

## Inputs

CFBD:

```text
GET /games?year=<season>&seasonType=both&classification=fbs
```

SportsDataverse / ESPN-native:

```text
espn_cfb_schedules season asset
```

Exact game IDs and C1 V4 participant-orientation rules are prerequisites.

## Context fields

### Venue identity

Compare:

```text
CFBD venueId
ESPN-native venue_id
```

A shared external venue ID is strong delivery-path crosswalk evidence but never becomes canonical Daily-NCAAF `VENUE_ID`.

Venue display strings are compared separately because sponsor/branding names may drift:

```text
CFBD venue
ESPN-native venue
```

### Neutral-site state

Compare:

```text
CFBD neutralSite
ESPN-native neutral_site
```

Provider home/away assignment remains non-canonical even when `neutral_site == false`.

### Participant classification

After C1 participant orientation:

```text
CFBD homeClassification / awayClassification
ESPN-native home_division / away_division
```

Classification is a program-season/context state, not program identity.

### Participant conference

After C1 participant orientation:

```text
CFBD homeConference / awayConference
ESPN-native home_conference / away_conference
```

Conference labels are observations tied to the event/season context and must not overwrite canonical `CONFERENCE_AFFILIATION_STINT` history without reconciliation.

### Conference-game semantics

Compare separately:

```text
CFBD conferenceGame
ESPN-native conference_competition
```

These flags may encode different semantics. A mismatch is a semantic observation, not automatically a bad record or identity failure.

## Required per-season evidence

```text
CFBD FBS-involved game rows
ESPN-native schedule rows
exact shared game IDs
CFBD exact-ID coverage
participant orientation states

venue-id state counts
venue-name state counts
neutral-site state counts
home/away classification state counts
home/away conference state counts
conference-game-flag state counts

field-specific mismatch examples
source asset hash + advertised digest + acquired_at
```

## Comparison states

Identifier / boolean fields:

```text
MATCH
MISMATCH
UNAVAILABLE
```

Text fields:

```text
EXACT
NORMALIZED
MISMATCH
UNAVAILABLE
```

Participant context may also be:

```text
UNRESOLVED_ORIENTATION
```

## Production concepts being tested

```text
VENUE
VENUE_PROVIDER_CROSSWALK
GAME_VENUE_OBSERVATION
GAME_CONTEXT_OBSERVATION
CONFERENCE_AFFILIATION_STINT
CLASSIFICATION_STINT
```

The production schema must preserve raw event-context observations before deriving canonical context.

## Safety rules

```text
provider venue ID != canonical VENUE_ID
venue display-name change != venue identity break
conference label != PROGRAM identity
conference change != new PROGRAM
classification change != new PROGRAM
neutral-site flag != home/away identity authority
conferenceGame flag != conference affiliation proof
shared upstream origin != independent corroboration
cross-delivery agreement != PIT safety
```

## C5 freeze candidate criteria

C5 may freeze when:

1. exact matched events provide enough venue/context evidence across 2023-2025;
2. participant-side comparison always uses C1 orientation semantics;
3. venue-ID disagreements are zero or individually explained;
4. classification/conference disagreements are quantified and never silently normalized away;
5. neutral-site disagreements are explicit;
6. conference-game flag disagreements remain a separate semantic class rather than being treated as affiliation failures;
7. provider/upstream provenance remains explicit;
8. canonical venue/conference/classification identities remain provider-independent.
