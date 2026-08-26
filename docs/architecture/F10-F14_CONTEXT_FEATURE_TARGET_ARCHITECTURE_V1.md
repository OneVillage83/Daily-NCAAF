# Daily NCAAF Context, Feature & Target Architecture

**The Daily Line — Daily NCAAF**  
**F-10 through F-14 — Version 1.0**  
**Status: LOCKED V1**

## Purpose

This document defines the contextual state engines, feature contract system, and prediction-target architecture for Daily NCAAF. The goal is to ensure that every model input has explicit meaning, provenance, point-in-time semantics, missingness behavior, and versioning before it becomes model-ready.

---

# F-10 — Injury & Availability State Engine

## F-10.1 Observation is not latent truth

Separate:

```text
AVAILABILITY_OBSERVATION
        ↓
LATENT_PLAYER_AVAILABILITY_STATE
```

An observation may contain player, reported status, source, published timestamp, availability timestamp, reliability, and confidence. It does not directly equal exact game participation or exact player effectiveness.

## F-10.2 College reporting quality is uneven

The engine must support:

- program-specific reporting quality
- provider disagreement
- missing status information
- uncertain depth charts
- late decisions
- incomplete historical coverage

Missing information must not default to healthy or unchanged.

## F-10.3 Latent availability outputs

Candidate outputs include:

- `P(available)`
- `P(starts)`
- expected snap share
- expected role
- expected effectiveness conditional on playing
- availability uncertainty

## F-10.4 Scenario propagation

Critical availability uncertainty should create scenarios that flow into unit state and simulation rather than one fixed penalty.

Example:

```text
Starter plays normally      0.60
Starter plays limited       0.20
Backup starts               0.20
```

## F-10.5 Source reliability is learnable

Track source/provider timing, accuracy, correction rate, and program-level behavior so future availability inference can weight evidence empirically.

## F-10.6 Depth-chart relationship

Published depth charts, expected-starter probabilities, and observed participation remain distinct data families.

## F-10.7 PIT rule

Final game participation never backfills earlier pregame snapshots as if it had been known.

**F-10 status: LOCKED V1.**

---

# F-11 — Weather, Venue, Surface & Home-Environment State

## F-11.1 Core boundary

`Daily-Data-Core` owns generic weather acquisition, venue coordinates, time zones, and raw forecast snapshots. `Daily-NCAAF` converts those inputs into college-football context.

## F-11.2 Candidate environment features

- temperature
- wind speed/direction
- gusts
- precipitation
- humidity
- pressure where useful
- indoor/outdoor
- roof state where applicable
- playing surface
- altitude
- daylight/time-of-day context

## F-11.3 Forecast uncertainty

Pregame weather is a forecast distribution, not final observed game weather. Preserve forecast timestamp and revision history.

## F-11.4 Home field is heterogeneous

Do not hard-code one universal NCAAF home-field constant. Allow research into program/venue-specific effects conditioned on opponent, travel, altitude, crowd/context, season, and data era.

## F-11.5 Neutral-site context

Officially neutral games may still be geographically or behaviorally asymmetric. Preserve official designation and derive contextual features separately.

Potential features include:

- campus-to-venue distance for both teams
- time zones
- venue familiarity
- regional proximity
- conference geography

## F-11.6 Surface/venue history

Venue and surface changes are time-versioned. Historical games must reference the venue state valid at the time.

**F-11 status: LOCKED V1.**

---

# F-12 — Travel, Rest & Recovery State Engine

## F-12.1 Shared primitives, NCAAF interpretation

Daily Data Core may compute generic distance, time-zone, geospatial, and calendar primitives. Daily NCAAF owns college-football interpretation and feature research.

## F-12.2 Candidate travel/rest state

- travel distance
- time zones crossed
- body-clock offset proxies
- days since prior game
- bye-week state
- short-week state
- consecutive away games
- prior-game location
- altitude transition
- schedule sequencing
- neutral-site travel for both teams

## F-12.3 Recovery is not one scalar

Future research may combine travel, previous workload, prior-game intensity, overtime, roster depth, and rest into recovery state. The architecture should not require a fixed travel penalty.

## F-12.4 Postseason travel

Bowls, conference championships, and CFP games may create materially different travel/preparation contexts and should remain identifiable.

## F-12.5 PIT requirements

Only schedule/travel information knowable by the prediction time may enter historical snapshots. Later itinerary detail must not leak backward.

**F-12 status: LOCKED V1.**

---

# F-13 — Complete NCAAF Feature Architecture

## F-13.1 Feature families

Daily NCAAF should support versioned feature families including:

```text
PROGRAM PERFORMANCE
PLAYER STATE
UNIT STATE
MATCHUPS
COACHING
SCHEME
AVAILABILITY
WEATHER
VENUE / HOME CONTEXT
TRAVEL / REST / RECOVERY
OPPONENT STRENGTH
STRENGTH OF SCHEDULE
RECRUITING / TALENT
TRANSFER PORTAL
RETURNING PRODUCTION
ROSTER CONTINUITY
EXPERIENCE / ELIGIBILITY
SPECIAL TEAMS
PACE
BIG-PLAY CREATION / PREVENTION
SUCCESS RATE / EFFICIENCY
FINISHING DRIVES
PRESSURE / DISRUPTION
FIELD POSITION
TURNOVER PROCESS
FOURTH-DOWN POLICY
RED-ZONE STATE
LOW-LEVERAGE / RESERVE CONTEXT
CONFERENCE / CLASSIFICATION CONTEXT
RULESET / ERA
DATA QUALITY / MISSINGNESS
MARKET — only in eligible market-aware families
```

## F-13.2 Every feature requires a contract

A model-ready feature must have a registry/contract containing at least:

```text
feature_name
definition
unit
grain
source family
calculation
required inputs

available_from
available_to
availability rule
PIT classification

missingness rule
imputation policy
quality flags

feature_version
validation/tests
```

A feature without a defensible PIT contract is not model-ready.

## F-13.3 Grain is explicit

Features may exist at program, program-game, player, player-game, unit, matchup, drive, play, or prediction-snapshot grain. Joins across grains require explicit aggregation rules.

## F-13.4 Missingness policy is feature-specific

Possible policies include:

- no imputation / model missingness directly
- hierarchical shrinkage
- prior distribution
- program/conference/level fallback
- explicit missing indicator
- feature unavailable for that era

Do not use one global imputation rule.

## F-13.5 Era/coverage awareness

A feature can be valid only for seasons/providers where evidence exists. Models trained across long history must know which feature era applies.

## F-13.6 Football-only vs market feature namespace

Market-derived features must be clearly tagged so football-only models cannot accidentally import them.

## F-13.7 Derived ratings and retrospective inputs

External ratings or reconstructed metrics require PIT classification. Retrospective-only ratings can be research benchmarks but are forbidden as historical pregame features unless historical availability can be established.

## F-13.8 Dependency graph

Each feature should declare upstream dependencies so material pregame changes trigger only affected recalculation where practical.

Conceptually:

```text
Observation change
      ↓
Affected state
      ↓
Affected features
      ↓
Affected models
      ↓
New immutable prediction snapshot
```

## F-13.9 Feature lineage

Feature snapshots must link back to source evidence and versioned transformations sufficiently to reproduce published predictions.

**F-13 status: LOCKED V1.**

---

# F-14 — Prediction Targets & Label Architecture

## F-14.1 Model underlying football distributions

The system should prefer coherent underlying targets over isolated sportsbook-line classifiers.

Primary game targets include:

- home win / away win
- home score
- away score
- margin
- total

Derived probabilities can then be computed at arbitrary supported market lines.

## F-14.2 Initial market outputs

Initial production-compatible market families:

- moneyline
- spread
- game total

Later expansion may include:

- team totals
- first half
- first quarter
- alternative lines
- player markets
- drive/scoring-event markets

## F-14.3 Labels are separate from market settlement

Football outcome labels describe what happened on the field. Sportsbook settlement describes how a quote/selection grades. The two are linked but not interchangeable.

## F-14.4 Score-distribution coherence

Models should eventually maintain logical coherence among win probability, margin, total, and team-score distributions rather than generating mutually contradictory isolated estimates.

## F-14.5 Player targets

Future player targets may include passing, rushing, receiving, touchdowns, sacks/pressure-related outcomes where defensible, and participation-conditioned distributions.

Player targets must condition on availability/role uncertainty rather than assuming guaranteed participation.

## F-14.6 Drive/play targets

Future simulation may model:

- next play execution
- yards/outcome distribution
- first-down probability
- turnover probability
- drive scoring outcome
- field-position transition
- drive length/time

## F-14.7 Label finalization and corrections

Official corrections create versioned truth records. Historical predictions remain unchanged.

## F-14.8 Unsupported-market behavior

If a market lacks the minimum target/data contract, Daily NCAAF records it as unsupported for that model/version rather than fabricating a low-quality prediction.

## F-14.9 Every eligible supported game is predicted

Coverage is universal within the declared support contract. Recommendation status does not determine whether a forecast exists.

**F-14 status: LOCKED V1.**

---

# F-10 through F-14 Definition of Done

Implementation must eventually support probabilistic availability, forecast-aware environment state, travel/rest context, a complete versioned feature registry with PIT/missingness contracts, dependency-aware recalculation, coherent football targets, and strict separation between football labels and market settlement.

**F-10 through F-14: LOCKED V1.**
