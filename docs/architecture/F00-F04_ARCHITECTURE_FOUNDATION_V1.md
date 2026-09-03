# Daily NCAAF Architecture Foundation

**The Daily Line — Daily NCAAF**  
**F-0 through F-4 — Version 1.0**  
**Status: LOCKED V1**

## Purpose

This document establishes the scientific, domain, data, identity, and historical point-in-time foundation for Daily NCAAF before implementation begins.

Daily NCAAF is a college-football-specific intelligence engine under The Daily Line. Cross-sport infrastructure belongs in `Daily-Data-Core`; college-football-native domain logic, state reconstruction, features, models, and simulation belong in `Daily-NCAAF`.

The architecture is deliberately production-oriented from the beginning. Initial implementation may stage capabilities over time, but it must not intentionally violate or bypass the final contracts described here.

> **Critical PIT rule:** There is no blanket prohibition on Saturday, game-day, or late pregame data. Any information may be used if its defensible availability timestamp is at or before the prediction snapshot timestamp and strictly before official kickoff. Daily NCAAF should continue to observe meaningful pregame changes through kickoff. Information first available after kickoff is excluded from that pregame prediction.

---

# Governing Decisions

| Decision | Locked Rule | Owner |
|---|---|---|
| Repository boundary | Sport-agnostic infrastructure belongs in `Daily-Data-Core`; NCAAF intelligence belongs in `Daily-NCAAF`. | Core / NCAAF |
| Architecture strategy | Build the production architecture first; do not knowingly create disposable MVP contracts. | NCAAF |
| Prediction philosophy | Estimate calibrated outcome distributions, not merely picks. | NCAAF |
| Coverage | Predict every eligible supported game/market; Recommendation Gate decides BET / LEAN / PASS / AVOID afterward. | Core + NCAAF |
| Provider rule | Providers populate canonical contracts; provider schemas never become the architecture. | Core + NCAAF |
| Evidence rule | Immutable raw evidence precedes normalization and feature engineering. | Core |
| Identity rule | Canonical internal IDs are authoritative; provider IDs are versioned crosswalks. | Core + NCAAF |
| PIT rule | Every feature must be defensible as knowable by the prediction snapshot timestamp. | Core + NCAAF |
| Pregame monitoring | Continue observing meaningful roster, availability, weather, schedule, venue, and market changes until kickoff. | Core + NCAAF |
| Historical rule | Final retrospective truth and historical knowledge state are separate. | NCAAF |
| College hierarchy | FBS/FCS, conferences, conference membership, postseason structures, and neutral-site semantics are explicit/versioned. | NCAAF |
| Transfer rule | Player identity persists across school changes; transfer is a stint/state transition, not a new person. | NCAAF |
| Opponent adjustment | Strength of opposition is a central modeling primitive, not an optional feature. | NCAAF |
| Evaluation | Primary final validation is chronological / walk-forward. | NCAAF |
| Shared football rule | Build NFL and NCAAF separately, then extract only abstractions proven semantically common. | NFL + NCAAF |

---

# Repository Boundary: Daily-Data-Core vs Daily-NCAAF

The Daily Line should have one cross-sport platform and sport-native intelligence engines.

## Daily-Data-Core owns

- provider/provenance primitives
- immutable raw evidence addressing and checksums
- acquisition run/job lifecycle
- generic observation/revision semantics
- generic identity/crosswalk primitives
- sportsbooks, odds, markets, market quotes, and quote history
- implied probability and no-vig utilities
- weather acquisition and forecast snapshots
- venues, coordinates, and time zones
- generic travel-distance/time-zone primitives
- generic prediction record primitives
- Recommendation Gate contract primitives
- settlement/performance ledger primitives
- common failure/retry/reliability metadata

## Daily-NCAAF owns

- college-football competition ontology
- FBS/FCS and level/classification history
- school/program/program-season identity
- conference and conference-membership history
- schedules, games, phases, weeks, bowls, CFP, championship games
- rosters, roster/eligibility stints, transfers, recruiting, returning production
- college player/team/coach reconciliation rules
- injuries and availability observations
- depth-chart and expected-participation state
- possessions, drives, plays, events, participation
- program/team state
- player state
- unit state
- coaching/scheme state
- opponent-strength and schedule-strength state
- garbage-time/substitution state
- NCAAF feature contracts
- NCAAF model targets
- NCAAF prediction models
- NCAAF simulation
- NCAAF-specific evaluation and research

A future shared-football package may exist only after Daily NFL and Daily NCAAF demonstrate truly shared semantics in production implementations.

---

# F-0 — Scientific Mission & Modeling Philosophy

**Status: LOCKED V1**

## F-0.1 Primary mission

Daily NCAAF exists to estimate the **true probability distribution of future college-football outcomes using only information legitimately available at the prediction time**.

Sports betting is the immediate application, but the deeper problem is:

> Given everything defensibly knowable at time T, what distribution of possible college-football games can occur?

The system should therefore evolve toward a coherent game-state representation capable of supporting many markets from one underlying probabilistic football model.

Long-term outputs may include:

- `P(home win)` / `P(away win)`
- expected home/away score
- score distributions
- margin distribution
- total distribution
- cover probability at arbitrary supported spreads
- over/under probability at arbitrary supported totals
- team-total distributions
- first-half / first-quarter distributions
- player-stat distributions
- drive and scoring-event distributions
- alternative-line probabilities
- eventually joint/dependency structures for correlated markets

## F-0.2 Predict everything; recommend selectively

Every eligible supported game receives predictions. Every supported market receives a prediction whenever its minimum data contract is satisfied.

```text
Football State
    ↓
Prediction
    ↓
Probability Distribution
    ↓
Fair Price
    ↓
Market Comparison
    ↓
Edge / EV
    ↓
Uncertainty / Risk
    ↓
Recommendation Gate
    ↓
BET / LEAN / PASS / AVOID
```

The Recommendation Gate must never decide whether a prediction exists.

PASS and AVOID predictions remain first-class records and must be stored, settled, calibrated, and evaluated.

## F-0.3 Optimization hierarchy

The model-quality hierarchy is:

1. Data correctness
2. Point-in-time correctness
3. Probability calibration
4. Distributional accuracy
5. Generalization
6. Market discrimination
7. Closing-line value
8. Betting profitability

Short-run W/L record alone is not an acceptable scientific objective.

Evaluation may include:

- log loss
- Brier score
- calibration error/curves
- CRPS or related distributional scoring rules
- interval coverage
- score/margin MAE or RMSE
- CLV
- ROI
- performance by uncertainty/confidence band
- performance by conference, week, favorite size, venue state, season era, data-quality tier, prediction horizon, and market type

## F-0.4 College football is a hierarchical state system

A program is not adequately represented by a single rating.

Daily NCAAF should represent interacting state across:

- quarterback room
- offensive line
- running backs
- receivers/tight ends
- defensive front
- pass rush
- linebackers
- secondary
- special teams
- coaching/play calling
- scheme
- personnel usage
- injuries/availability
- depth
- recruiting/talent priors
- transfers
- returning production
- eligibility/experience
- opponent quality
- rest/travel
- environment

Long-term direction:

```text
Player State
    ↓
Unit State
    ↓
Program State
    ↓
Matchup State
    ↓
Play / Drive Models
    ↓
Game Simulation
    ↓
Market Probabilities
```

## F-0.5 Separate football information from market information

Maintain explicit forecasting tracks:

### FOOTBALL_ONLY

Uses football/context information but excludes sportsbook market features.

### MARKET_ONLY

Uses market information as an explicit benchmark/forecasting family.

### MARKET_AWARE

May incorporate opening price, consensus, movement, dispersion, timing, and related market signal.

### ENSEMBLE

Combines eligible model families while preserving lineage and attribution.

The system must never compare a sportsbook line against a disguised reconstruction of that same line without acknowledging market input.

## F-0.6 Uncertainty is first-class

Represent where applicable:

- predictive variance
- model uncertainty
- input uncertainty
- availability uncertainty
- depth-chart/participation uncertainty
- roster-transition uncertainty
- data-quality uncertainty
- simulation uncertainty

A 60% mean forecast with known starters and strong data is not equivalent to a 60% forecast with unresolved quarterback status and weak injury reporting.

## F-0.7 Continuous research architecture

Expected progression:

```text
Baseline Team Models
      ↓
Opponent-Adjusted Models
      ↓
Roster / Talent Transition Models
      ↓
Player / Unit State Models
      ↓
Drive / Play Models
      ↓
Sequence / Graph Models
      ↓
Tracking / Film / Spatial Models
      ↓
College Football World Model
```

New research should augment the architecture without forcing platform replacement.

## F-0.8 Reproducibility

Every published prediction should eventually be reproducible from:

- model/version
- code commit
- feature-contract version
- source dataset/provider versions
- raw evidence IDs/checksums
- feature snapshot
- prediction timestamp
- market snapshot
- configuration
- ruleset version
- random/simulation seed where relevant

---

# F-1 — NCAAF Domain Ontology

**Status: LOCKED V1**

## F-1.1 Core hierarchy

```text
Sport
  ↓
Competition
  ↓
Classification / Level
  ↓
Season
  ↓
Season Phase
  ↓
Week
  ↓
Game
  ↓
Possession
  ↓
Drive
  ↓
Play
  ↓
Play Event
  ↓
Participation
```

The canonical hierarchy models football reality rather than mirroring one provider.

## F-1.2 School, program, and program-season are distinct

```text
School
  ↓
Program
  ↓
Program Season
```

`School` represents the institution. `Program` represents the football program identity. `ProgramSeason` represents season-specific competitive state.

Program-season state may contain:

- classification/level
- conference affiliation
- home venue
- coaching regime
- roster context
- schedule context
- season-specific naming/abbreviation

## F-1.3 Conference affiliation is a historical stint

Conference identity must not be a timeless column on `Program`.

Conceptually:

```text
Program
  ↓
Conference Affiliation Stint
  ├─ conference_id
  ├─ effective_from
  ├─ effective_to
  └─ source/provenance
```

This is mandatory because realignment changes both competition structure and historical interpretation.

## F-1.4 Competition and classification are explicit

Represent at minimum:

- NCAA football competition
- FBS
- FCS
- supported lower divisions if later added
- regular season
- conference championship
- bowl
- College Football Playoff
- other postseason/exhibition states where applicable

Cross-level games must remain identifiable rather than being silently mixed with same-level games.

## F-1.5 Game is separate from result

`Game` represents the scheduled sporting event. Result/final truth is separate.

Game may include:

- internal game ID
- season/week/phase
- home program-season
- away program-season
- venue
- scheduled kickoff
- actual kickoff
- status
- official neutral-site flag
- postseason/bowl/CFP metadata

Result may include:

- final scores
- period scores
- overtime state
- winner
- finalization timestamp
- correction version

Final-result information must not be placed where pregame feature queries can accidentally consume it.

## F-1.6 Official neutral site is not equivalent to neutral advantage

Store the official designation separately from derived contextual neutrality.

Potential contextual features include:

- distance from each campus
- regional proximity
- expected fan split proxies
- historical venue familiarity
- travel/time zones
- conference geography

The model may discover a non-zero advantage even when `neutral_site = true`.

## F-1.7 Person is separate from player/program stint

```text
Person
  ↓
Player
  ↓
Player Program Stint
```

Identity must survive:

- transfers
- jersey-number changes
- position changes
- redshirts
- eligibility-year changes
- provider-ID changes
- naming-format changes

A transfer creates a new relationship/state, not a new person.

## F-1.8 Eligibility and roster relationship are explicit state

College player state may require:

- roster membership
- eligibility year
- redshirt state
- transfer state
- suspension/disciplinary state where defensibly sourced
- expected participation
- active/inactive equivalents where available

The schema must tolerate incomplete or uncertain eligibility information rather than invent certainty.

## F-1.9 Player state

Long-term player state may include:

- talent prior
- current performance
- role
- snap share
- usage
- health
- availability
- workload
- experience
- eligibility
- team-conditioned performance
- position-specific skill
- uncertainty

Player state always means state **as of prediction time**.

## F-1.10 Unit state

Initial unit concepts:

- quarterback room
- offensive line
- receiving unit
- backfield
- defensive front
- edge/pass rush
- linebacker unit
- secondary
- coverage unit
- special teams

## F-1.11 Coaching and scheme are modeled entities/state

Support staff identity and role:

- head coach
- offensive coordinator
- defensive coordinator
- special-teams coordinator
- play caller
- later position coaches when evidence justifies it

Scheme state may include:

- pace/tempo
- neutral pass rate
- motion
- RPO
- play action
- option/QB run
- personnel usage
- blitz rate
- coverage families
- fourth-down aggressiveness
- red-zone behavior

Coaching changes are explicit historical events.

## F-1.12 Injury report is observation, not truth

An injury/availability report is an observation carrying a source, timestamp, reliability, and uncertainty. It is not direct measurement of exact ability.

Daily NCAAF may infer latent availability using observations, historical participation, role, practice/status information where available, source reliability, and later richer data.

## F-1.13 Depth chart is not actual participation

Separate:

- published depth chart
- expected-starter probability
- expected snap share
- observed participation

This is especially important in college due to uncertain depth charts, rotations, blowouts, and large talent cliffs.

---

# F-2 — Data Source & Acquisition Architecture

**Status: LOCKED V1**

## F-2.1 Provider abstraction

No public library, API, website, feed, or commercial vendor becomes the architecture.

```text
Daily-NCAAF Application
        ↓
Domain Service
        ↓
Provider Capability Interface
        ↓
Provider Adapter(s)
```

The model layer should never depend directly on a specific provider schema.

## F-2.2 Provider capability registry

Each provider/dataset should eventually have machine-readable metadata including:

- provider
- dataset
- entity coverage
- field coverage
- seasons covered
- update cadence
- expected latency
- historical availability
- PIT fidelity
- reliability tier
- schema version
- license/terms metadata
- attribution requirements
- cost class
- known limitations

## F-2.3 Source families

### Tier A — Foundational historical college-football data

Potential capabilities include:

- schedules/games/results
- play-by-play
- drives
- teams/programs/conferences
- rosters/players
- statistics
- advanced statistics
- recruiting
- transfers
- returning production
- coaches
- rankings/ratings

Specific providers are implementation choices behind interfaces.

### Tier B — Daily Data Core

Daily NCAAF consumes cross-sport inputs including:

- odds/markets
- sportsbook quotes/history
- no-vig/fair-market utilities
- weather
- venues
- coordinates/time zones
- travel/rest primitives
- provenance
- immutable evidence
- run lifecycle
- settlement primitives

### Tier C — Live/pre-kickoff college state

Provider adapters should support as available:

- schedule updates
- roster changes
- injuries/availability
- depth-chart changes
- suspensions/eligibility changes
- quarterback/start decisions
- venue changes
- weather changes
- game status

### Tier D — Enrichment

Future capabilities may include:

- advanced charting
- participant-level play data
- tracking/spatial data
- film/computer vision
- biomechanical/mechanical state
- commercial feeds

## F-2.4 Raw evidence first

Required pattern:

```text
Provider
   ↓
Raw Response / Raw Artifact
   ↓
Immutable Evidence Store
   ↓
Normalization
   ↓
Canonical NCAAF Schema
   ↓
State / Feature Engineering
```

Direct provider-to-feature pipelines are forbidden for production data unless the raw evidence is preserved elsewhere with equivalent lineage.

## F-2.5 Acquisition metadata

Each raw artifact should preserve where applicable:

- acquisition_run_id
- provider
- endpoint/dataset
- request parameters
- requested_at
- received_at
- HTTP/status metadata
- provider-reported timestamp
- checksum/content hash
- content type
- schema/version hint
- success/failure state
- retry lineage

## F-2.6 Provider disagreement is retained

When sources disagree, do not destructively choose one value without evidence. Preserve observations and run reconciliation with explicit confidence/source rules.

## F-2.7 Missingness is data

College football has uneven reporting quality. Missing injury/depth/roster information may depend on program, season, provider, and timing. Missingness must be represented rather than silently interpreted as normal/healthy/unchanged.

## F-2.8 Licensing and attribution are data attributes

Store provider licensing/attribution metadata with source registry records so future commercial publication/research workflows can enforce source requirements.

---

# F-3 — Canonical Identity & Reconciliation

**Status: LOCKED V1**

## F-3.1 Internal IDs are primary

Canonical entities receive Daily Line IDs independent of provider IDs.

Examples:

- `school_id`
- `program_id`
- `program_season_id`
- `conference_id`
- `conference_affiliation_id`
- `person_id`
- `player_id`
- `player_program_stint_id`
- `coach_id`
- `coach_program_stint_id`
- `venue_id`
- `game_id`
- `drive_id`
- `play_id`

Provider IDs are stored as crosswalks.

## F-3.2 Crosswalks are time-aware where necessary

Conceptual structure:

```text
PROVIDER_ENTITY_CROSSWALK

canonical_entity_type
canonical_entity_id
provider
provider_entity_type
provider_entity_id
valid_from
valid_to
confidence
resolution_method
created_at
```

## F-3.3 Program identity rules

Identity reconciliation should tolerate:

- school naming variants
- abbreviations
- historical names
- provider aliases
- conference changes
- venue changes
- reclassification

A conference move must never create a new program identity.

## F-3.4 Player identity rules

Identity resolution can use evidence such as:

- provider IDs
- full name/normalized name
- school/program stint
- position
- jersey
- class/eligibility
- hometown/high school where available
- dates/season overlap

Jersey number alone is never a stable identity key.

## F-3.5 Transfer reconciliation

A transfer should conceptually look like:

```text
PLAYER
  ├─ Program A Stint
  └─ Program B Stint
```

Preserve transfer dates/availability timestamps where defensible.

## F-3.6 Game identity

Game reconciliation may use:

- season
- participating program-seasons
- scheduled kickoff
- venue
- week/phase
- provider IDs

Schedule revisions must not accidentally create duplicate canonical games.

## F-3.7 Reconciliation is auditable

Store resolution method and confidence for non-trivial matches. Ambiguous identities should be surfaced for review rather than silently guessed.

---

# F-4 — Historical Point-in-Time & Pregame Monitoring Architecture

**Status: LOCKED V1**

## F-4.1 Core PIT eligibility

For a pregame prediction snapshot:

```text
available_at <= prediction_time < kickoff
```

Only information defensibly available by that snapshot may enter its feature state.

## F-4.2 Event truth vs knowledge state

Separate:

### Event truth

What ultimately happened.

### Historical knowledge state

What was knowable at a historical time.

Example: a final starting quarterback may be obvious after the game, but a prediction made six hours before kickoff may have faced uncertainty. Historical reconstruction must preserve that uncertainty rather than backfill the final starter as if it was already known.

## F-4.3 Timestamp semantics

Observations should preserve where applicable:

- `observed_at`
- `published_at`
- `available_at`
- `acquired_at`
- `valid_from`
- `valid_to`
- `corrected_at`

`available_at` is the governing prediction-eligibility time when defensible.

## F-4.4 Retrospective datasets require PIT classification

Modern datasets may contain values recomputed retrospectively using later information. Such values may be useful for descriptive analysis but cannot automatically become historical pregame features.

Every dataset/feature family should receive a PIT fidelity classification such as:

- `NATIVE_PIT`
- `RECONSTRUCTABLE_PIT`
- `RETROSPECTIVE_ONLY`
- `UNKNOWN`

## F-4.5 Prediction snapshots are immutable

Material new information produces a new snapshot.

Example:

```text
T-24h Prediction A
T-6h  Prediction B
T-90m Prediction C
T-20m Prediction D
```

Prediction D never overwrites A-C.

## F-4.6 Standard checkpoint families

Useful checkpoints may include:

- T-7d
- T-72h
- T-24h
- T-6h
- T-90m
- T-30m

These do not replace event-driven recalculation.

## F-4.7 Event-driven recalculation

Material observations may trigger recalculation for affected games, including:

- quarterback availability/start change
- major injury/availability update
- depth-chart change
- eligibility/suspension update
- meaningful weather revision
- venue/kickoff change
- coaching/play-caller change
- significant market movement

The dependency graph should recompute only affected state/features when practical.

## F-4.8 No blanket game-day exclusion

Information legitimately available before kickoff remains eligible, regardless of whether it arrived on Saturday, Friday night, or minutes before kickoff.

## F-4.9 Post-kickoff information is excluded from pregame models

The cutoff is the game start, not the calendar day.

## F-4.10 Revision semantics

If a source later corrects a historical observation, preserve:

- original observation
- correction
- correction timestamp
- revised canonical truth where appropriate

Do not mutate historical published prediction inputs.

## F-4.11 Historical feature materialization

Historical feature generation should occur from time-aware source observations, not from current-state tables joined backward without temporal constraints.

## F-4.12 PIT testing is mandatory

The implementation must eventually include tests designed to fail if:

- post-kickoff fields enter pregame features
- final results leak into game features
- future roster/transfer/availability state appears early
- retrospective ratings are mislabeled as historical knowledge
- later depth/starting information overwrites earlier uncertainty

---

# F-0 through F-4 Definition of Done

This layer is architecturally complete when implementation can eventually guarantee:

1. a provider-independent domain model;
2. immutable raw evidence and provenance;
3. canonical school/program/player/coach/game identity;
4. versioned conference/classification history;
5. transfer-safe player identity;
6. explicit retrospective-vs-PIT dataset classification;
7. immutable historical prediction snapshots;
8. continuous pregame observation through kickoff;
9. automated leakage/PIT tests;
10. a clean boundary between `Daily-Data-Core` and `Daily-NCAAF`.

**F-0 through F-4: LOCKED V1.**
