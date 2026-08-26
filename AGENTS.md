# AGENTS.md — Daily NCAAF

This file defines repository-level guardrails for human and AI contributors.

## Governing architecture

Read `docs/architecture/README.md` and the applicable F00-F24 document before implementing or modifying a subsystem.

The architecture documents are authoritative V1 contracts. Do not silently reinterpret them in code. If implementation exposes a real architectural conflict, document the issue and propose a versioned architecture change.

## Non-negotiable rules

1. Build toward the full production architecture; do not introduce deliberate disposable-MVP shortcuts that contradict the documented contracts.
2. Predict every eligible supported game/market before the Recommendation Gate acts.
3. BET / LEAN / PASS / AVOID are downstream recommendation states.
4. PASS and AVOID predictions remain stored, settled, and evaluated.
5. Pregame feature eligibility requires `available_at <= prediction_time < kickoff`.
6. There is no blanket prohibition on same-day information; legitimately available pre-kickoff information is eligible.
7. Published/historical prediction snapshots are immutable. New information creates new snapshots.
8. Preserve immutable raw provider evidence before normalization/feature engineering.
9. Internal canonical IDs are authoritative; provider IDs are crosswalks.
10. Provider schemas do not define domain architecture.
11. Retrospective truth and historical knowledge state are distinct.
12. External/derived ratings require PIT classification before use in historical pregame features.
13. Conference membership, classification, coaching regimes, roster/eligibility stints, venues, and rulesets are time-versioned where applicable.
14. Player identity persists through transfer, school change, jersey change, position change, and eligibility change.
15. Opponent and schedule-strength adjustment are central NCAAF primitives.
16. Football-only, market-only, market-aware, and ensemble forecasts remain explicitly distinguishable.
17. Market-derived features must never leak into football-only models.
18. Primary final validation is chronological/walk-forward.
19. New models enter challenger/shadow evaluation and earn promotion.
20. Do not train future football models only on BET selections.
21. Cross-sport infrastructure belongs in `Daily-Data-Core`.
22. Do not prematurely extract shared NFL/NCAAF code. Extract only after both implementations prove equivalent semantics.

## Implementation discipline

- Add/modify tests with behavior changes.
- Keep schemas/migrations versioned and reversible where practical.
- Preserve provenance and lineage for all derived artifacts.
- Prefer explicit typed contracts over provider-specific dictionaries leaking through the codebase.
- Make missingness and uncertainty explicit rather than inventing certainty.
- Record failed acquisitions and reconciliation ambiguity rather than silently dropping them.
- Avoid final-result or later-known state in pregame query paths.
- Keep research artifacts distinct from historical public predictions.

## Documentation discipline

When a meaningful implementation or scientific decision is made:

- update the relevant architecture/implementation/data/model documentation;
- add an ADR when the decision changes a significant contract or tradeoff;
- version locked architecture rather than silently rewriting it;
- record rejected research hypotheses where useful.

## Initial implementation order

```text
Architecture
  ↓
Source / Coverage Audit
  ↓
Canonical Schema
  ↓
Identity / Reconciliation
  ↓
Raw Evidence / Provenance
  ↓
Historical PIT Foundation
  ↓
Play / Drive Normalization
  ↓
State Engines
  ↓
Feature Contracts
  ↓
Baseline Models
  ↓
Advanced Models
  ↓
Simulation
  ↓
Markets / Recommendation Gate
  ↓
Settlement / Evaluation / Continuous Learning
```
