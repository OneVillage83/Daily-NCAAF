# Daily NCAAF — TDL Unified Ensemble Overlay V1

Status: **governing cross-sport overlay for Daily NCAAF**

Date locked: 2026-09-12

This document adopts the cross-sport TDL Unified Forecasting architecture for college football and is intended to sit alongside the F00–F24 governing architecture referenced by the repository.

## 1. Canonical NCAAF forecast hierarchy

```text
NCAAF non-market evidence
        |
        +--> multiple team-strength / rating systems
        +--> Elo / power ratings
        +--> logistic / GLM / GAM
        +--> hierarchical Bayesian team/roster models
        +--> XGBoost / LightGBM / CatBoost
        +--> roster / QB / player-state models
        +--> coaching / scheme models
        +--> matchup specialists
        +--> injury / availability specialists
        +--> weather / venue / travel specialists
        +--> possession / drive / score simulation
        |
        v
Dynamic learned independent ensemble
        |
        v
Calibration
        |
        v
TDL NCAAF Unified Line
        |
        +--> fair moneyline
        +--> fair spread
        +--> fair total
        +--> score / cover / O-U distributions
        |
        v
Market Intelligence + NCAAF Line Timing Model
        |
        v
Residual / EV / uncertainty / Recommendation Gate
```

## 2. College-football multi-rating metamodel

NCAAF should explicitly preserve diversity among rating systems rather than choose one universal power rating.

The model registry may contain:

- Elo variants;
- SRS;
- Massey-style systems;
- Colley-style systems;
- opponent-adjusted efficiency ratings;
- recruiting/talent priors;
- roster continuity ratings;
- QB-adjusted ratings;
- coaching/system continuity ratings;
- custom TDL team-strength systems.

The Unified Ensemble learns which rating families add unique forward predictive information and which are redundant.

## 3. Early-season hierarchy

College football has unusually large early-season uncertainty because schedules are short, roster turnover is large, coaching/system changes can be material, and many teams have sparse current-season evidence.

The dynamic ensemble should therefore support context-dependent weight shifts such as:

```text
EARLY SEASON
hierarchical priors / talent / continuity   UP
multi-year team-strength                     UP
small-sample current-season raw statistics DOWN

LATER SEASON
current-season efficiency                    UP
opponent-adjusted performance                UP
preseason prior influence                  SHRINK
```

These shifts must be learned/validated rather than manually assumed forever.

## 4. Model Zoo

### Rating / strength systems
- Elo and variants
- SRS
- Massey
- Colley
- opponent-adjusted efficiency
- custom TDL power ratings
- roster/talent/continuity ratings

### Statistical
- logistic regression
- GLM/GAM
- mixed-effects
- hierarchical models
- state-space/dynamic models

### ML
- Random Forest / Extra Trees
- XGBoost
- LightGBM
- CatBoost
- SVM and future challengers

### Football-native
- EPA/success-rate model
- QB/player-state model
- roster/depth model
- coaching/scheme model
- matchup model
- weather/venue model
- travel/rest/recovery model
- drive/score simulation

### Representation / specialist
- clustering/regime detection
- PCA/latent representations
- conference/style specialists
- early-season specialist
- weather specialist
- roster-turnover specialist

## 5. Dynamic Learned Ensemble Importance

NCAAF model weights vary by:

- target;
- season phase;
- data/sample maturity;
- roster/QB certainty;
- coaching continuity;
- matchup regime;
- model diversity;
- uncertainty;
- current data quality;
- prediction horizon.

A model that is weak across the full season may still be retained if it proves uniquely valuable in early-season, high-roster-turnover, weather, conference/style, or other validated contexts.

## 6. TDL NCAAF Unified Line

The independent NCAAF output is calibrated after the dynamic ensemble and before any market comparison.

Example structure:

```text
Elo / Power               ...
SRS / rating family       ...
Hierarchical Bayesian     ...
Logistic / GLM            ...
XGBoost                   ...
LightGBM                  ...
EPA / efficiency          ...
Roster/QB model           ...
Simulation                ...
Specialists               ...

Independent ensemble      ...
TDL Unified Line          ...
```

## 7. Market firewall

The TDL NCAAF Unified Line does not consume sportsbook, exchange, prediction-market, line-movement, or closing-line features.

Market evidence enters only after the independent line exists.

## 8. NCAAF Line Timing Model

The Line Timing Model is especially important in college football because the information content of the market changes materially from open to close.

DDC owns the normalized market timeline. Daily-NCAAF owns `NCAAF-LTM`.

Required evaluation:

```text
TDL fair spread
    vs opening
    vs current
    vs consensus
    vs closing (post-hoc only)
```

The LTM should learn whether a current TDL disagreement tends to be absorbed by the market before kickoff and whether the best execution is likely to exist now or later.

Candidate NCAAF LTM features include:

- time since open / time to kickoff;
- magnitude of TDL-vs-open disagreement;
- cross-book dispersion;
- sharp/soft divergence;
- QB/roster news timing;
- injury/availability information;
- weather forecast evolution;
- conference/team liquidity profile;
- key-number proximity;
- prediction-market divergence where available.

Candidate outputs:

```text
expected close
P(spread moves toward TDL)
P(crosses key number)
expected line CLV now
expected price CLV now
BET_NOW / WAIT
```

## 9. Opening-line research must remain honest

If NCAAF demonstrates greater edge against opening prices than closing prices, that is evidence about information timing, not permission to use future closing information when generating opening-time forecasts.

Every historical opening-time evaluation must reconstruct only information available at that timestamp.

## 10. Specialist discovery

Candidate NCAAF specialties include:

- early-season games;
- new coach/system;
- high roster turnover;
- QB uncertainty;
- FBS/FCS or large strength mismatches;
- conference/style interactions;
- travel/timezone extremes;
- weather extremes;
- rivalry/rematch contexts only if forward evidence supports them;
- tempo/style mismatch;
- late-season injury/depth attrition.

The registry should preserve specialist contribution even when aggregate ranking is mediocre.

## 11. Out-of-fold / calibration rules

Base models feed the stacker only through frozen forward/OOF predictions. Calibration uses isolated out-of-sample evidence. Final test evidence is not reused as a tuning set.

Randomly shuffled cross-validation is not the primary proof for production NCAAF forecasting.

## 12. Immutable prediction ledger

Every prediction snapshot remains permanently linked to:

- cutoff time;
- model/version;
- feature snapshot;
- roster/injury state;
- weather state;
- independent model vector;
- Unified Line;
- later market movement;
- close;
- result.

This lets NCAAF answer whether early forecasts, later forecasts, or specific information updates provide the strongest signal.

## 13. Governing rule

> Daily NCAAF combines many rating, statistical, machine-learning, football-native, and simulation experts, but a model receives influence only where forward point-in-time evidence proves unique value. The independent calibrated result is the TDL NCAAF Unified Line; market timing and decision logic remain a separate layer.
