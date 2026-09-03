# Daily NCAAF Recommendation, Learning, Extensions & World Model Architecture

**The Daily Line — Daily NCAAF**  
**F-20 through F-24 — Version 1.0**  
**Status: LOCKED V1**

## Purpose

This document completes the governing Daily NCAAF architecture through F-24. It defines the Recommendation Gate, settlement/continuous-learning loop, NCAAF-specific extensions, the future NFL/NCAAF shared-football extraction rule, and the long-term College Football World Model research charter.

System-wide rules remain unchanged:

- predictions exist before recommendation decisions;
- BET / LEAN / PASS / AVOID never determine whether a forecast is stored;
- PASS and AVOID are settled and evaluated;
- pregame PIT eligibility is `available_at <= prediction_time < kickoff`;
- historical predictions are immutable;
- football-only, market-only, market-aware, and ensemble predictions remain auditable;
- model promotion is evidence-based rather than driven by short-run ROI.

---

# F-20 — Recommendation Gate Architecture

## F-20.1 Mission

The Gate does not decide what Daily NCAAF predicts. It decides whether an existing forecast and a specific current market quote represent a sufficiently strong, reliable, and risk-aware opportunity to recommend.

```text
FOOTBALL STATE
      ↓
MODEL
      ↓
PROBABILITY DISTRIBUTION
      ↓
FAIR PRICE
      ↓
MARKET COMPARISON
      ↓
EDGE / EV
      ↓
UNCERTAINTY / RISK
      ↓
RECOMMENDATION GATE
      ↓
BET / LEAN / PASS / AVOID
```

## F-20.2 Prediction and recommendation are separate objects

`PREDICTION` stores the model artifact, inputs, feature snapshot, prediction time, probabilities/distributions, uncertainty, and lineage.

`RECOMMENDATION_DECISION` references an existing prediction plus a specific market quote.

Conceptual fields:

```text
recommendation_id
prediction_id
market_quote_id
as_of
model_probability
market_probability
probability_edge
expected_value
model_uncertainty
data_uncertainty
availability_uncertainty
model_disagreement
quote_age
edge_stability
gate_version
decision
reason_codes
created_at
```

## F-20.3 Canonical states

- `BET` — sufficient evidence to recommend.
- `LEAN` — directional preference but not full BET criteria.
- `PASS` — insufficient risk-adjusted value.
- `AVOID` — apparent value may exist, but conditions are especially unreliable or unsuitable.

## F-20.4 PASS/AVOID never erase forecasts

Every recommendation state remains linked to a stored prediction and later outcome/market settlement.

## F-20.5 Gate inputs

Potential inputs include:

- model probability
- fair market probability
- edge / EV
- model uncertainty
- input/data uncertainty
- QB/availability uncertainty
- depth-chart uncertainty
- roster-transition uncertainty
- weather uncertainty
- data quality
- model disagreement
- calibration-region evidence
- prediction horizon
- quote freshness
- market dispersion
- edge stability
- provider/quote quality

## F-20.6 College-specific uncertainty matters

The Gate should be able to treat the following as distinct from ordinary model variance:

- weak program injury reporting
- unresolved QB competition
- incomplete FCS data
- early-season roster uncertainty
- major coaching transition
- late eligibility/availability uncertainty

The Gate may reduce recommendation confidence without rewriting the model's original football probability.

## F-20.7 Edge stability

Track edge history rather than only final magnitude. Candidate metrics include edge mean, variance, direction changes, largest revision, and recent revision. Whether stability is predictive is an empirical research question.

## F-20.8 Model disagreement

Preserve disagreement among component models. Two identical ensemble means with very different component spreads should not be treated as identical confidence states.

## F-20.9 Structured reason codes

Initial families may include:

```text
EDGE_BELOW_THRESHOLD
EV_BELOW_THRESHOLD
HIGH_MODEL_DISAGREEMENT
HIGH_AVAILABILITY_UNCERTAINTY
HIGH_ROSTER_UNCERTAINTY
STALE_MARKET
LOW_DATA_QUALITY
CALIBRATION_RISK
LINE_MOVED_PAST_VALUE
STRONG_EDGE_HIGH_CONFIDENCE
```

Multiple codes may apply.

## F-20.10 Transparent Gate V1

Initial Gate logic should be explicit/deterministic with thresholds validated on prior data. A learned Gate can be tested later against this stable control.

## F-20.11 Historical decisions are immutable

If a line moves, the old recommendation remains historically intact and the new quote receives a new decision.

## F-20.12 Bet sizing is separate

Keep recommendation separate from bankroll/portfolio sizing. Future sizing research may include flat staking, fractional Kelly, uncertainty-adjusted Kelly, and correlation-aware exposure.

**F-20 status: LOCKED V1.**

---

# F-21 — Settlement & Continuous Learning Loop

## F-21.1 Closed-loop system

```text
PREDICTION
   ↓
RECOMMENDATION
   ↓
GAME
   ↓
FOOTBALL TRUTH
   ↓
MARKET SETTLEMENT
   ↓
MODEL EVALUATION
   ↓
GATE EVALUATION
   ↓
RESEARCH / RETRAINING
```

## F-21.2 Three distinct ledgers

Maintain:

```text
FOOTBALL_RESULT_LEDGER
MARKET_SETTLEMENT_LEDGER
MODEL_PERFORMANCE_LEDGER
```

Football truth, sportsbook grading, and model performance are related but not interchangeable.

## F-21.3 Football result ledger

Preserve final score, period scores, overtime, winner, finalization state, correction lineage, and eventually drive/play/player truth.

## F-21.4 Market settlement ledger

For every evaluated quote, store market/selection/line/price/book and settlement state such as WIN / LOSS / PUSH / VOID under a versioned settlement rule.

## F-21.5 Settle every recommendation state

BET, LEAN, PASS, and AVOID predictions should all be analyzable against game truth and market outcome. This enables direct testing of whether the Gate adds value.

## F-21.6 Closing market is separate truth

Preserve closing quote/consensus/no-vig probability separately from final game result. This supports two different questions:

1. Did the model beat the market?
2. Did the model predict football well?

## F-21.7 Corrections are versioned

Official stat/result corrections create new truth versions. Published predictions never change retroactively.

## F-21.8 Learning lineage

Research datasets may combine prediction, feature snapshot, football truth, market snapshot, closing market, and recommendation decision without losing provenance.

## F-21.9 Retraining is policy-driven

Support versioned policies such as weekly, every N games, monthly, season-boundary, drift-triggered, or research-only retraining.

## F-21.10 No Gate-selection training bias

Never train future football models only on BET selections. The Gate is a decision layer, not the definition of football reality.

## F-21.11 Negative research results remain recorded

Maintain research decisions such as PROMOTE / REJECT / RETEST / DEFER with experiment lineage.

## F-21.12 Provider-quality learning

Measure latency, coverage, correction rate, identity failures, availability accuracy, and PIT fidelity by provider/source.

## F-21.13 Drift monitoring

Monitor feature drift, data-coverage drift, calibration drift, and concept drift. College football changes through rules, transfer behavior, conference structure, coaching trends, and scheme evolution.

## F-21.14 Shadow learning loop

Champion models create public predictions. Challengers create shadow predictions. All are settled/evaluated prospectively under the same truth universe.

**F-21 status: LOCKED V1.**

---

# F-22 — NCAAF-Specific Extensions

F-22 contains college-football concepts that should remain in Daily NCAAF rather than being pushed into Daily Data Core or a generic football package.

## F-22.1 FBS/FCS hierarchy

Represent classification explicitly and version it historically. Cross-level games must remain identifiable for strength adjustment, coverage, and evaluation.

## F-22.2 Conference realignment

Conference membership is a time-bounded affiliation. Historical conference features must use the membership valid in that season.

## F-22.3 Recruiting and team-talent priors

Recruiting information may inform low-sample player/program priors. Recruiting is not equivalent to proven college performance and must carry uncertainty.

## F-22.4 Transfer portal

Track transfers in/out as player-program relationship changes. Preserve talent evidence while re-estimating role, scheme, teammates, and competition context.

## F-22.5 Returning production

Offseason priors may use returning snaps/starts, QB experience, OL continuity, skill-position production, defensive continuity, and special-teams continuity.

## F-22.6 Departures

Differentiate graduation, eligibility exhaustion, transfer departure, professional departure, retirement/other departure where defensibly known. The mechanism may affect priors and uncertainty.

## F-22.7 Eligibility/redshirt state

Eligibility year, redshirt status, and related state should be supported without assuming perfect historical coverage.

## F-22.8 Coaching carousel

Track head coach, coordinators, play callers, interim changes, and regime effective dates. College staff turnover is frequent enough to require first-class treatment.

## F-22.9 Bowl and CFP availability

Postseason participation can differ from regular season due to departures, transfers, coaching changes, and player decisions. Build a distinct postseason availability state rather than assuming the regular-season roster persists unchanged.

## F-22.10 Early-season uncertainty

Weeks 0-4 require special research into prior-season carryover, roster transitions, recruiting, transfers, staff changes, and limited current-season evidence.

## F-22.11 Strength-of-schedule centrality

Because schedules are highly heterogeneous, opponent/schedule adjustment is a central college architecture primitive, not a secondary feature family.

## F-22.12 Low-leverage and reserve-heavy play

Support game-state/participation-aware weighting so large late-game margins do not automatically contaminate starter/team-state estimates.

## F-22.13 Scheme diversity

College-specific scheme state must accommodate tempo extremes, option concepts, RPO-heavy systems, spread systems, power systems, QB-run-heavy systems, and other structurally different styles.

## F-22.14 Neutral-site asymmetry

Official neutrality and effective contextual neutrality are separate. Venue proximity, travel, regional support, and familiarity may produce asymmetric effects.

## F-22.15 Rivalry context

Rivalry designation may be retained as context, but no arbitrary rivalry multiplier is assumed. Predictive value must come from underlying mechanisms or validated empirical evidence.

## F-22.16 Polls/rankings

Polls and rankings may contain information about public/market perception. They must be time-stamped and assigned to football-only or market/perception feature families explicitly rather than silently mixed.

## F-22.17 College ruleset history

Version clock, overtime, replay, kickoff, eligibility, and other rule changes. Historical simulation must use the effective era.

## F-22.18 Data-quality regimes

College data quality varies by season, program, level, and provider. Data-quality state should be available to models/evaluation and the Recommendation Gate.

**F-22 status: LOCKED V1.**

---

# F-23 — NFL/NCAAF Shared-Football Extraction Architecture

## F-23.1 Governing rule

Do not extract shared football code merely because Daily NFL and Daily NCAAF use similar words. Build both implementations and compare actual semantics first.

## F-23.2 Likely conceptual overlap

Potential shared concepts include:

- Game / Drive / Play
- Play Execution
- Participation
- Player State interfaces
- Unit State interfaces
- Team State interfaces
- Coaching State interfaces
- environment/travel interfaces
- feature-contract primitives
- prediction/simulation/evaluation interfaces

Conceptual overlap does not guarantee shared implementation.

## F-23.3 Known semantic differences

Examples:

```text
NFL Franchise ≠ NCAAF Program
NFL roster mechanics ≠ college eligibility/portal mechanics
NFL injury reporting ≠ college information environment
NFL postseason ≠ bowl/CFP structure
NFL draft/free agency ≠ recruiting/transfer ecosystem
```

## F-23.4 Extraction test

A component is eligible for shared-football extraction when:

1. both implementations exist;
2. inputs/outputs carry the same semantics;
3. lifecycle/PIT behavior is the same;
4. tests demonstrate equivalent behavior;
5. extraction reduces duplication without forcing sport-specific exceptions into generic code.

## F-23.5 Destination

Only proven cross-football abstractions should move to a future shared package. Cross-sport infrastructure remains in Daily Data Core. Sport-specific state remains in its sport repository.

## F-23.6 No inheritance hierarchy for cosmetic similarity

Prefer composition/contracts over deep sport-class inheritance. A generic abstraction should exist because behavior is genuinely common, not because both sports have a thing named `Team`.

**F-23 status: LOCKED V1.**

---

# F-24 — College Football World Model Research Charter

## F-24.1 Long-term goal

Daily NCAAF should evolve toward a football-native probabilistic world model that represents how player, unit, team, matchup, environment, coaching, and game state interact over time.

It is not an LLM replacement for structured models. It is a structured/learned simulation system grounded in football state.

## F-24.2 State hierarchy

```text
PLAYER STATE
     ↓
UNIT STATE
     ↓
PROGRAM STATE
     ↓
MATCHUP STATE
     ↓
PLAY STATE
     ↓
DRIVE STATE
     ↓
GAME STATE
     ↓
PROBABILISTIC NEXT STATE
```

## F-24.3 Candidate world state

Future state may include:

- formation/personnel
- field position
- down/distance
- clock/score
- player availability/talent
- fatigue/workload
- unit configurations
- coaching policy
- scheme/matchup
- weather/surface
- travel/recovery
- opponent tendencies
- ruleset

## F-24.4 Candidate next-state outputs

The system may eventually estimate distributions for:

- next play execution family
- play result
- possession continuation
- drive result
- field-position transition
- scoring event
- next game state
- final score

These transitions can be rolled forward through Monte Carlo/game simulation.

## F-24.5 College-specific world-model challenges

The research program must account for:

- wide talent disparity
- rapidly changing rosters
- sparse low-level player evidence
- transfer-induced state changes
- scheme diversity
- uneven schedules
- low-leverage substitutions
- variable information quality
- historical ruleset changes

## F-24.6 Research layers

Potential progression:

```text
Team score distributions
      ↓
Drive-state models
      ↓
Play-state models
      ↓
Player/unit-conditioned transitions
      ↓
Sequence models
      ↓
Spatial/film-derived state
      ↓
College Football World Model
```

## F-24.7 Research discipline remains unchanged

World-model complexity never overrides PIT correctness, reproducibility, calibration, champion/challenger governance, or the requirement to beat simpler controls out of time.

**F-24 status: LOCKED V1.**

---

# Architecture Completion

Daily NCAAF V1 is architecturally complete through **F-24**.

The next phase is implementation planning and source/coverage validation, not architecture reinvention. Implementation should proceed from truth/evidence and PIT foundations toward football state, features, baselines, advanced models, simulation, markets, recommendation, and continuous learning.

Future changes must be versioned rather than silently rewriting this V1 contract.

**F-20 through F-24: LOCKED V1.**
