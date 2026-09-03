# Daily NCAAF Model, Simulation, Market & Evaluation Architecture

**The Daily Line — Daily NCAAF**  
**F-15 through F-19 — Version 1.0**  
**Status: LOCKED V1**

## Purpose

This document defines the model ladder, advanced-model architecture, simulation path, sportsbook-market separation, calibration/backtesting constitution, and model-promotion rules for Daily NCAAF.

The system is designed to evolve from strong transparent baselines toward player/unit-conditioned game simulation and eventually a college-football world model without replacing the evidence, identity, PIT, or feature-contract foundations.

---

# F-15 — Baseline Model Ladder

## F-15.1 Baselines are permanent controls

Simple models remain in the evaluation harness even after stronger systems exist. They provide scientific controls and detect whether additional complexity creates real out-of-time value.

## F-15.2 Baseline ladder

Recommended families:

```text
B0 — Naive historical baselines
B1 — Elo / SRS-like strength model
B2 — Opponent-adjusted efficiency model
B3 — Offense/defense score model
B4 — Gradient-boosted game model
B5 — Hierarchical college model
B6 — Early-season roster/talent transition model
B7 — Calibrated ensemble
```

The exact sequence can evolve, but the system must maintain multiple independent controls.

## F-15.3 Naive controls

Useful controls may include:

- home-team historical win rate
- simple score average
- prior-season program rating
- conference/level priors

These are not production aspirations; they quantify the value added by later models.

## F-15.4 Elo/SRS-like rating

A transparent dynamic team-strength model is valuable because it establishes whether more complex state modeling improves on a strong low-dimensional baseline.

College-specific adjustments may include:

- opponent quality
- home/neutral context
- cross-level games
- season transition/mean reversion

## F-15.5 Opponent-adjusted efficiency baseline

A central baseline should estimate offense and defense quality after schedule adjustment. Raw yards/points are insufficient because college opponent quality is highly heterogeneous.

## F-15.6 Score model

Build a model capable of producing expected team scores or a joint score distribution so moneyline, spread, and total estimates arise from related football outputs.

## F-15.7 Gradient-boosted game model

A tree-based model may combine program state, opponent-adjusted efficiency, context, roster state, coaching, availability, and travel/environment features while preserving feature/version lineage.

## F-15.8 Hierarchical college model

The architecture should support partial pooling such as:

```text
National
  ↓
Classification / Level
  ↓
Conference / Schedule Ecosystem
  ↓
Program
  ↓
Game / Matchup
```

Conference effects are time-versioned because membership and relative strength change.

## F-15.9 Early-season roster/talent model

Weeks 0-4 may rely more heavily on:

- previous-season state
- returning production
- quarterback continuity
- transfer additions/losses
- recruiting/talent priors
- coaching/scheme changes
- departures

As current-season evidence grows, data should progressively overwhelm priors according to validated update rules.

## F-15.10 Market-only benchmark

Maintain an explicit market-only baseline. If complex football models fail to improve calibration, distributional accuracy, or useful market discrimination beyond the market benchmark, the system should detect that honestly.

**F-15 status: LOCKED V1.**

---

# F-16 — Advanced Model Architecture

## F-16.1 Multiple model families are expected

Candidate advanced families include:

- dynamic state-space models
- hierarchical Bayesian models
- gradient-boosted trees
- player aggregation models
- unit models
- matchup interaction models
- graph/network opponent models
- temporal sequence models
- drive-level models
- stacking/ensembles
- scenario-mixture models

No family is promoted because it is fashionable; it must win scientific evaluation.

## F-16.2 Dynamic Roster Transition Model

A major NCAAF-specific research target is the offseason transition from prior team state to new-season prior:

```text
Prior Season State
      ↓
Graduation / Eligibility Loss
NFL Departures
Transfers Out
Transfers In
Recruiting
Returning Production
QB Continuity
Coaching / Scheme Changes
      ↓
New Season Prior Distribution
```

The output should be a distribution with uncertainty, not a single arbitrary offseason rating.

## F-16.3 Player-to-unit-to-team aggregation

Long-term architecture should permit:

```text
Player State
    ↓
Unit Configuration
    ↓
Unit State
    ↓
Team / Program State
```

This enables availability changes to propagate structurally rather than via fixed point deductions.

## F-16.4 Matchup interaction models

Advanced models should be able to represent opponent-conditioned interactions such as protection vs rush, QB vs pressure, receivers vs coverage, run structure vs defensive front, tempo vs depth, and special-teams field-position interactions.

## F-16.5 Graph/network opponent modeling

College schedules form an uneven network. Graph-based or hierarchical methods may help infer program strength across weakly connected schedule regions, especially early season and across classifications.

## F-16.6 Temporal sequence models

Sequence models may eventually operate on drives, plays, personnel, or state transitions. They must respect chronological training and PIT feature eligibility.

## F-16.7 Ensemble architecture

Ensembles should preserve component forecasts and weights. A final probability must not erase model disagreement.

Store where practical:

- component model IDs/versions
- component predictions
- ensemble method/version
- weights
- disagreement metrics

## F-16.8 Champion/challenger separation

Advanced research models do not immediately become public models. They enter a challenger/shadow framework governed by F-19.

**F-16 status: LOCKED V1.**

---

# F-17 — Simulation Engine

## F-17.1 Simulation roadmap

```text
Score-Distribution Simulation
          ↓
Drive Simulation
          ↓
Play Simulation
          ↓
Player / Unit Conditioned Simulation
          ↓
College Football World Model
```

Each stage should produce useful distributions while remaining compatible with later richer state.

## F-17.2 Monte Carlo outputs

Simulation may produce:

- final score distribution
- margin distribution
- total distribution
- win probability
- spread-cover probabilities
- total-over/under probabilities
- team totals
- period distributions
- player distributions when supported

## F-17.3 Availability scenarios

Critical uncertainty should be represented through scenario mixtures.

Example:

```text
QB starts normally  0.70
QB limited          0.15
Backup starts       0.15
```

Run scenario-conditioned forecasts and aggregate by scenario probability rather than forcing one guessed lineup.

## F-17.4 State transitions

Drive/play simulation should eventually condition on:

- field position
- down/distance
- clock
- score
- timeouts where relevant
- offense/defense state
- player/unit availability
- coaching policy
- scheme/matchup state
- environment
- ruleset

## F-17.5 Coaching policy in simulation

Decision policies for fourth down, two-point attempts, tempo, field goals/punts, and clock management should be modelable rather than fixed universally.

## F-17.6 Ruleset-specific simulation

Historical simulation must use rules valid for the season/phase being modeled, including college overtime/clock changes.

## F-17.7 Simulation reproducibility

Persist model/version, scenario set, configuration, random seed, sample count, and input snapshot IDs so simulation output can be reproduced.

## F-17.8 Simulation accuracy is evaluated distributionally

Do not judge simulation only by winner accuracy. Evaluate score/margin/total distributions, interval coverage, calibration, and downstream market probabilities.

**F-17 status: LOCKED V1.**

---

# F-18 — Betting Market Architecture

## F-18.1 Market data belongs in Daily-Data-Core

Core owns generic sportsbook, market, quote, price, timestamp, consensus, no-vig, and movement primitives. Daily NCAAF owns how football forecasts interact with those markets.

## F-18.2 Four explicit forecasting families

```text
FOOTBALL_ONLY
MARKET_ONLY
MARKET_AWARE
ENSEMBLE
```

Every prediction identifies its family.

## F-18.3 Initial supported markets

Initial architecture supports:

- moneyline
- spread
- game total

Later, when underlying targets are scientifically adequate:

- team totals
- first half
- first quarter
- alternate lines
- player props
- drive/scoring-event markets

## F-18.4 Quote identity matters

A recommendation references a specific market quote, including book, market, selection, line, price, and timestamp. A later line/price is a new opportunity state.

## F-18.5 No-vig and consensus

Generic implied-probability and no-vig calculations belong in Core. NCAAF evaluation should preserve individual-book and consensus views rather than collapsing the market too early.

## F-18.6 Market movement is historical evidence

Preserve opening, intermediate, current, and closing quotes where available. Movement features are time-indexed and only eligible in market-aware models.

## F-18.7 College market efficiency is empirical

Measure market behavior by:

- conference
- program
- market type
- favorite/underdog size
- time to kickoff
- early/late season
- FBS/FCS context
- home/away/neutral state
- market-dispersion/liquidity proxies

Do not assume NFL-like efficiency or timing.

## F-18.8 Independent football edge must remain measurable

The system must always retain a football-only track so we can ask whether football information adds value beyond the sportsbook market.

**F-18 status: LOCKED V1.**

---

# F-19 — Calibration, Backtesting & Model Promotion Constitution

## F-19.1 Primary evaluation metrics

Use appropriate measures including:

- log loss
- Brier score
- calibration curves/error
- CRPS or related distributional scores
- interval coverage
- score/margin MAE/RMSE where appropriate
- CLV
- ROI

Profitability is important but does not override probabilistic quality and validity.

## F-19.2 Chronological validation

Primary evaluation is out of time:

```text
Train on past
   ↓
Validate on later period
   ↓
Roll forward
   ↓
Repeat
```

Random row splitting is not the primary final validation method.

## F-19.3 Season boundaries and regime changes

Backtests should preserve real season transitions, roster turnover, coaching changes, conference realignment, ruleset changes, and feature-availability eras.

## F-19.4 Evaluation slices

At minimum, inspect performance by:

- season/week
- early vs late season
- conference
- FBS/FBS and FBS/FCS
- favorite size
- home/away/neutral
- prediction horizon
- weather/context band where relevant
- coaching transition
- QB/availability uncertainty
- roster continuity
- data-quality tier
- market type

## F-19.5 Calibration before confidence language

Recommendation/confidence labels must be connected to empirical calibration. A nominal 70% region should be tested for actual frequency rather than trusted because the model outputs 0.70.

## F-19.6 Model disagreement is retained

For ensembles, preserve disagreement metrics such as component range, standard deviation, and pairwise differences. Similar ensemble means can hide very different model-consensus states.

## F-19.7 Champion/challenger lifecycle

```text
RESEARCH
   ↓
CHALLENGER
   ↓
SHADOW PREDICTIONS
   ↓
PROSPECTIVE EVIDENCE
   ↓
PROMOTION REVIEW
   ↓
CHAMPION
```

## F-19.8 Promotion requirements

A challenger should demonstrate, as applicable:

- no PIT/leakage violations
- stable reproducibility
- improved or non-inferior calibration
- improved distributional quality
- reasonable subgroup behavior
- prospective/shadow evidence
- acceptable operational reliability
- clear feature/data lineage

Short hot-streak ROI is insufficient.

## F-19.9 Negative results are retained

Record rejected features/models/hypotheses so future research does not repeatedly rediscover failed ideas.

## F-19.10 Drift monitoring

Monitor feature drift, calibration drift, model error, data coverage, and concept drift. College football evolves through scheme, transfer behavior, conference structure, rules, and market participation.

## F-19.11 Retraining is not promotion

A retrained artifact becomes a challenger unless the governing promotion policy explicitly allows an equivalent routine refresh under a validated procedure.

## F-19.12 Final holdout integrity

Research iteration must not repeatedly optimize against the final evaluation period. Maintain clear train/validation/test or rolling evaluation governance.

**F-19 status: LOCKED V1.**

---

# F-15 through F-19 Definition of Done

Implementation must eventually maintain permanent simple controls, opponent-adjusted/hierarchical baselines, a versioned advanced-model registry, scenario-aware simulation, explicit football-only vs market-aware separation, chronological probabilistic evaluation, shadow challengers, and evidence-based promotion.

**F-15 through F-19: LOCKED V1.**
