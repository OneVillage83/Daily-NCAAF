# Daily NCAAF — Definition of Done

This document defines the production-level completion criteria for Daily NCAAF. Individual milestones may ship before the entire system reaches this state, but no partial milestone should redefine the final architecture downward.

## 1. Evidence & provenance

- Major production providers are registered with coverage, licensing, reliability, and PIT metadata.
- Raw provider responses/artifacts are preserved immutably with checksums and acquisition lineage.
- Normalized records can be traced back to source evidence.
- Failed/retried acquisitions remain auditable.

## 2. Canonical identity

- Schools, programs, program-seasons, conferences, conference affiliations, people, players, player-program stints, coaches, coach-role stints, venues, and games use internal canonical IDs.
- Provider IDs are crosswalks rather than primary domain identity.
- Transfers, jersey changes, position changes, and eligibility changes do not fragment player identity.
- Conference realignment is historically versioned.
- Schedule revisions do not create silent duplicate games.

## 3. Point-in-time correctness

- Pregame eligibility enforces `available_at <= prediction_time < kickoff`.
- Retrospective truth and historical knowledge state are structurally distinguishable.
- Prediction snapshots are immutable.
- Later-known starter, injury, transfer, result, ranking, or market information cannot leak into earlier snapshots.
- Automated PIT/leakage tests exist for critical feature families.

## 4. Football state

- Game/possession/drive/play/event state uses canonical provider-independent contracts.
- Program state is dynamic and opponent-adjusted.
- Player state separates transferable talent from program-conditioned state.
- Unit state supports depth and uncertain configurations.
- Coaching/scheme state is time-versioned.
- Availability is probabilistic/scenario-capable.
- Weather, venue, travel, rest, and neutral-site context are time-aware.
- Low-leverage/reserve-heavy evidence can be identified without deleting source data.

## 5. Feature system

- Every production feature has a versioned contract.
- Contracts define grain, source, calculation, PIT eligibility, missingness, imputation, coverage era, and lineage.
- Market features cannot enter football-only models accidentally.
- Feature snapshots are immutable/reproducible.
- Dependency-aware recalculation can create new snapshots after meaningful pregame changes.

## 6. Prediction targets

- Every eligible supported game receives predictions.
- Core score/margin/total/win targets are coherently represented.
- Unsupported markets are explicitly unsupported rather than guessed.
- Player/period/derived markets are added only when their minimum target/data contracts are satisfied.

## 7. Modeling

- Permanent simple baselines remain available for comparison.
- Opponent-adjusted and hierarchical college models are implemented.
- Early-season roster/talent transition uncertainty is represented.
- Football-only, market-only, market-aware, and ensemble predictions are separately identifiable.
- Model uncertainty/disagreement is retained.
- Model artifacts are versioned and reproducible.

## 8. Simulation

- At minimum, production simulation can produce calibrated game score/margin/total distributions.
- Critical availability uncertainty can be represented through scenarios.
- Simulation inputs, versions, seeds/configuration, and outputs are reproducible.
- Later drive/play simulation remains compatible with the same state architecture.

## 9. Market/value/recommendation

- Daily Data Core provides sportsbook quote/history primitives.
- Fair prices and no-vig comparisons are auditable.
- Recommendation Gate acts only after prediction/value/uncertainty evaluation.
- BET / LEAN / PASS / AVOID are immutable decision records referencing specific predictions and quotes.
- PASS and AVOID are stored and settled.
- Bet sizing remains a separate subsystem.

## 10. Settlement & learning

- Football result, market settlement, and model performance ledgers are distinct.
- Closing-line truth is preserved independently from game truth.
- All recommendation states are evaluated.
- Calibration, CLV, ROI, subgroup behavior, and Gate effectiveness can be measured.
- Retraining is policy-driven.
- Retraining does not automatically equal model promotion.
- Challenger/shadow predictions can be evaluated prospectively.
- Negative research results can be retained.

## 11. Evaluation constitution

- Primary final validation is chronological/walk-forward.
- Feature/ruleset/data eras are respected.
- Performance is sliced by major NCAAF regimes such as conference, week, FBS/FCS context, favorite size, venue state, prediction horizon, availability uncertainty, roster continuity, and data quality.
- Promotion requires probabilistic quality, PIT validity, reproducibility, and operational reliability—not a short winning streak.

## 12. Operations & reproducibility

Every published prediction can be traced to:

- prediction timestamp
- model/version
- code version
- feature-contract version
- feature snapshot
- source evidence IDs/checksums
- market snapshot
- ruleset version
- configuration
- simulation seed/configuration where applicable

Operational runs capture failures and can be resumed/retried safely where designed.

## 13. Publication

- Daily output covers every eligible supported game.
- Reports/APIs distinguish forecast from recommendation.
- Reason codes and uncertainty can be surfaced.
- Publication never rewrites historical prediction records.
- Performance reporting includes the full prediction universe, not only selected bets.

## 14. Shared-football extraction

Shared NFL/NCAAF code is extracted only after both implementations demonstrate semantically equivalent behavior and tests. Sport-specific behavior remains sport-specific.

## 15. Long-term research compatibility

The production foundation can evolve toward drive/play/player-conditioned simulation and a College Football World Model without replacing the canonical evidence, PIT, identity, feature, evaluation, or settlement architecture.

---

# Final acceptance principle

Daily NCAAF is not considered scientifically complete merely because it produces picks or positive ROI. Production completeness requires trustworthy historical knowledge reconstruction, calibrated distributions, reproducible forecasts, explicit uncertainty, auditable market comparison, complete settlement/evaluation, and a continuous-learning framework.
