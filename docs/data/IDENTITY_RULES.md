# Daily NCAAF — Canonical Identity & Reconciliation Rules V1

**Phase:** B — Source & Coverage Audit  
**Status:** GOVERNING IDENTITY RULES V1  
**Audit date:** 2026-08-26

## Purpose

College football identity is unusually dynamic. Programs change conferences and classifications; players transfer, change jersey numbers and positions; coaches change schools and roles; venues are renamed; games are rescheduled; provider IDs can disagree.

Daily NCAAF therefore owns canonical identities. Provider IDs are evidence and crosswalks, never the primary identity architecture.

---

# Governing identity principles

1. **Internal canonical IDs are authoritative.**
2. **Provider IDs are crosswalks.**
3. **Names are labels, never primary keys.**
4. **Time-varying membership/state is represented by stints, not overwritten entity fields.**
5. **A transfer does not create a new player.**
6. **A conference move does not create a new program.**
7. **Classification is program-season state, not permanent program identity.**
8. **Jersey number and position changes do not create new people.**
9. **Uncertain reconciliation remains unresolved rather than force-merged.**
10. **Merge/split corrections are auditable and reversible.**

---

# Canonical entity hierarchy

## Institutional / competitive identity

```text
SCHOOL
  -> PROGRAM
      -> PROGRAM_SEASON
          -> CONFERENCE_AFFILIATION_STINT
          -> CLASSIFICATION_STINT
          -> HOME_VENUE_STINT
```

### SCHOOL

Persistent institutional identity.

Example attributes may include canonical institution name and stable institutional metadata.

### PROGRAM

Persistent college-football competitive identity belonging to a school.

A program persists through:

- conference changes;
- FBS/FCS reclassification;
- nickname/abbreviation changes;
- stadium changes;
- coaching changes.

A school rename should normally create a new alias/version, not a new program, unless the underlying institution/program identity truly changed.

### PROGRAM_SEASON

Season-conditioned competitive state.

Examples:

```text
program_id
season
classification
conference affiliation
schedule context
coaching regime
roster state
```

This prevents today's conference/classification from leaking backward into historical games.

---

# Conference identity

Canonical objects:

```text
CONFERENCE
CONFERENCE_ALIAS
CONFERENCE_AFFILIATION_STINT
```

A program's conference is never stored as one timeless property.

Example:

```text
program_id = X
conference = A
valid_from = 2021 season
valid_to   = 2023 season

program_id = X
conference = B
valid_from = 2024 season
valid_to   = open
```

Provider evidence such as CFBD historical affiliations and conference-change effective years seeds these stints but does not replace our canonical temporal state.

Conference divisions, when applicable, are also time-versioned.

---

# Classification identity

Use a separate state family such as:

```text
PROGRAM_CLASSIFICATION_STINT

FBS
FCS
DIVISION_II
DIVISION_III
OTHER/UNKNOWN
```

Classification must not be hard-coded on the program record because programs can transition levels.

Games store the classification context of each participant at game time.

---

# Person and player identity

Canonical hierarchy:

```text
PERSON
  -> PLAYER
      -> PLAYER_PROGRAM_STINT
          -> PLAYER_SEASON_STATE
```

## PERSON

Persistent human identity.

## PLAYER

Football participant identity linked to the person.

## PLAYER_PROGRAM_STINT

A player's relationship to a program over a bounded interval.

A single player can therefore have:

```text
2024 Program A
2025 Program B
2026 Program B
```

without creating multiple canonical players.

## Transfer-safe identity

The following **must not** create a new player identity by themselves:

- transfer;
- jersey-number change;
- position change;
- redshirt season;
- eligibility-year change;
- name abbreviation change;
- punctuation/diacritic change;
- provider team change.

Transfer destination/origin belong to stints/events.

---

# Player identity evidence hierarchy

## Tier 1 — Strong deterministic evidence

Examples:

- exact stable provider athlete ID linked across seasons/teams;
- provider-declared team stints under one athlete ID;
- trusted cross-provider ID mapping;
- recruiting `athleteId` or roster-linked recruit identifier that resolves to the same athlete.

## Tier 2 — Strong composite evidence

Examples may combine:

```text
normalized full name
birth date if lawfully/appropriately available
prior school
new school
position
hometown
height/weight tolerance
recruit profile
transfer timing
```

Composite evidence still requires a confidence score.

## Tier 3 — Weak evidence

Examples:

- name only;
- name + jersey;
- name + position;
- fuzzy string match without contextual continuity.

Weak evidence can generate a **candidate match**, never an automatic identity merge.

---

# Name normalization rule

Normalization is used for blocking/search, not final identity.

Possible normalization:

```text
casefold
Unicode normalization
whitespace normalization
punctuation normalization
suffix parsing
common abbreviation handling
```

Never discard the original provider-rendered name.

Store aliases such as:

```text
PERSON_ALIAS
entity_id
alias_text
alias_type
provider
valid_from
valid_to
```

Two people named `J. Smith` remain two people unless stronger evidence connects them.

---

# Recruiting identity

Recruiting entities are provider observations and may precede canonical college player identity.

Conceptually:

```text
RECRUIT_OBSERVATION
  -> optional PLAYER linkage
```

Do not force a recruit into a player entity if linkage is uncertain.

When strong identifiers exist, preserve them:

```text
provider_recruit_id
provider_athlete_id
provider_player_id
```

as separate crosswalk identifiers.

Recruiting re-ratings are revisions to the recruiting observation, not new people.

---

# Transfer-portal identity

A portal entry is an event/observation:

```text
TRANSFER_PORTAL_OBSERVATION

player candidate identity
origin program
destination program if known
transfer/effective date
eligibility observation
rating/stars observation
source
availability timestamp
```

If a portal record contains only name/origin/destination without a stable athlete ID, it remains unresolved until sufficient evidence links it to a canonical player.

Forbidden behavior:

```text
portal row name == roster row name
=> automatic merge
```

This would create silent same-name collisions.

---

# Eligibility and redshirt state

Eligibility is **state**, not identity.

Possible future objects:

```text
PLAYER_ELIGIBILITY_OBSERVATION
PLAYER_ELIGIBILITY_STATE
REDSHIRT_STATE
```

A player does not receive a new identity because eligibility status changes.

Uncertain eligibility remains uncertain; do not encode missing as eligible.

---

# Coach identity

Canonical hierarchy:

```text
PERSON
  -> COACH
      -> COACH_ROLE_STINT
```

Role stint fields may include:

```text
program_id
role
start/effective date
end/effective date
interim flag
play-caller flag if known
source observations
```

Roles include at least:

```text
HEAD_COACH
OFFENSIVE_COORDINATOR
DEFENSIVE_COORDINATOR
SPECIAL_TEAMS_COORDINATOR
OFFENSIVE_PLAY_CALLER
DEFENSIVE_PLAY_CALLER
```

One coach can occupy multiple roles simultaneously.

CFBD head-coach IDs can seed canonical coach reconciliation, but Daily NCAAF must not invent OC/DC identities when those sources are absent.

## Interim coaches

Interim status is an attribute of the role stint, not a different person.

---

# Game identity

Canonical object:

```text
GAME
```

Provider IDs map through:

```text
PROVIDER_ENTITY_CROSSWALK
provider
entity_type = GAME
provider_entity_id
canonical_game_id
```

## Stable identity across schedule revisions

A game normally retains the same canonical identity through:

- kickoff-time changes;
- venue changes;
- broadcast changes;
- neutral-site designation corrections;
- postponement/rescheduling.

Cancellation state does not erase the game record.

If a postponed event is later recreated under a new provider ID, reconciliation determines whether it is the same scheduled contest or a newly constituted event.

## Game candidate matching

When provider game IDs differ, candidate matching may use:

```text
season
competition phase
home/away programs
scheduled date/time tolerance
venue
neutral-site context
```

Home/away labels are not always enough for neutral-site games, so team pair + competition context must remain primary evidence.

---

# Drive and play identity

Canonical:

```text
DRIVE
PLAY
PLAY_EVENT
PARTICIPATION
```

Provider event IDs remain crosswalks.

When reconciling CFBD and ESPN-derived PBP, do not assume play numbers align exactly. Candidate play reconciliation can use:

```text
game
drive sequence
period
clock
down
distance
yard line
score state
play text/execution
```

Because providers can insert/delete administrative plays or corrections, sequence number alone is insufficient.

Canonical event truth must support provider disagreement and correction revisions.

---

# Venue identity

Canonical:

```text
VENUE
VENUE_ALIAS
PROGRAM_HOME_VENUE_STINT
```

A naming-rights change should generally create an alias/version, not a new physical venue.

Material physical reconstruction/relocation may require a new venue identity or a geometry/facility version depending on whether the physical site changed.

Historical venue attributes such as surface, capacity, elevation/coordinates and dome state must be temporally versionable where they can change.

---

# Provider crosswalk contract

Generic object:

```text
PROVIDER_ENTITY_CROSSWALK

crosswalk_id
provider
provider_dataset
entity_type
provider_entity_id
canonical_entity_id
valid_from
valid_to
match_method
match_confidence
match_status
created_at
reviewed_at
```

Recommended match states:

```text
AUTO_CONFIRMED
MANUALLY_CONFIRMED
CANDIDATE
CONFLICT
REJECTED
SUPERSEDED
```

Provider IDs are never copied into internal foreign-key columns as a shortcut.

---

# Identity evidence ledger

Every nontrivial identity decision should be explainable.

Conceptual record:

```text
IDENTITY_EVIDENCE

candidate_a
candidate_b
evidence_type
evidence_value
source
weight
observed_at
resolution
resolver_version
```

This makes identity algorithms testable and allows later corrections without destroying provenance.

---

# Merge and split corrections

## Merge

If two canonical entities are later proven to be one:

- preserve both old IDs in an identity-history table;
- establish the surviving canonical identity;
- redirect future resolution;
- do not rewrite immutable raw provider evidence;
- version dependent canonical reconstructions.

## Split

If one canonical identity was incorrectly merging two people/programs/events:

- create the corrected identities;
- version the crosswalks;
- preserve the historical erroneous reconciliation record;
- recompute affected canonical state/features/models where required.

Never silently mutate historical reconciliation decisions.

---

# Identity confidence and model eligibility

An unresolved identity can affect model eligibility.

Example:

```text
transfer observation
player match confidence = LOW
```

Possible downstream behavior:

- preserve team-level transfer count with uncertainty if defensible;
- exclude player-specific talent transfer;
- increase roster uncertainty;
- emit data-quality reason code.

Never turn uncertain player identity into precise player features.

---

# Source-specific initial rules

## CFBD

- preserve CFBD game/team/player/coach/recruit IDs as provider crosswalks;
- use documented player `teamStints` as strong reconciliation evidence, not our only historical stint truth;
- use conference affiliation/effective-year records to seed canonical temporal membership;
- keep transfer-portal records as observations even when canonical player resolution is incomplete.

## SportsDataverse / ESPN-derived data

- preserve ESPN/event/player IDs separately from CFBD IDs;
- use participant/roster/game evidence for reconciliation;
- do not replace one provider ID with the other even when matched;
- retain raw provider representation for disagreement investigation.

## Official NCAA / program / conference sources

- official naming/competition records can resolve aliases and effective state;
- official text still becomes an evidence record rather than bypassing the canonical identity layer.

---

# Identity probe required in Phase B

Before Phase B closes, test at least:

1. players who remain at one school for several seasons;
2. one-transfer players;
3. multiple-transfer players;
4. same-name teammates/opponents;
5. jersey-number changes;
6. position changes;
7. recruit-to-college linkage;
8. portal entries lacking stable athlete ID;
9. coaches changing schools;
10. interim head coaches;
11. programs changing conferences;
12. classification transitions;
13. neutral-site games;
14. postponed/rescheduled games;
15. provider PBP disagreements.

Measure:

```text
auto-match precision
unresolved rate
false-merge rate
false-split rate
cross-provider match rate
provider-ID stability
```

High recall must never be achieved by accepting dangerous false merges.

---

# Locked consequence for Phase C

The future canonical database must support **entities + time-bounded stints + provider crosswalks + evidence-backed reconciliation** from the beginning.

A flat provider-shaped schema such as:

```text
players(team, name, jersey, position)
```

is explicitly insufficient for Daily NCAAF production architecture.
