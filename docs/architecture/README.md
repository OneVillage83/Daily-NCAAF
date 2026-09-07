# Daily NCAAF Architecture

**The Daily Line — Daily NCAAF**  
**Architecture Version: V1**

This directory contains the governing architecture references for Daily NCAAF. These documents are implementation contracts, not informal notes. Production code, research code, historical reconstruction, feature engineering, modeling, market evaluation, and future shared-football extraction must remain consistent with them unless a later version explicitly supersedes a rule.

## Governing documents

- [`F00-F04_ARCHITECTURE_FOUNDATION_V1.md`](./F00-F04_ARCHITECTURE_FOUNDATION_V1.md) — F-0 through F-4: scientific mission, NCAAF domain ontology, data-source architecture, canonical identity/reconciliation, historical point-in-time rules, and continuous pregame monitoring through kickoff.
- [`F05-F09_FOOTBALL_STATE_ARCHITECTURE_V1.md`](./F05-F09_FOOTBALL_STATE_ARCHITECTURE_V1.md) — F-5 through F-9: canonical game/drive/play architecture, Program/Team State Engine, Player State Engine, Unit State Engine, and Coaching & Scheme State Engine.
- [`F10-F14_CONTEXT_FEATURE_TARGET_ARCHITECTURE_V1.md`](./F10-F14_CONTEXT_FEATURE_TARGET_ARCHITECTURE_V1.md) — F-10 through F-14: Injury & Availability State Engine, Weather/Venue/Surface/Home Environment, Travel/Rest/Recovery, complete NCAAF feature taxonomy and contracts, and prediction targets/labels.
- [`F15-F19_MODEL_SIMULATION_MARKET_EVALUATION_ARCHITECTURE_V1.md`](./F15-F19_MODEL_SIMULATION_MARKET_EVALUATION_ARCHITECTURE_V1.md) — F-15 through F-19: baseline ladder, advanced models, Monte Carlo/drive/play simulation, market architecture, calibration/backtesting constitution, and model promotion.
- [`F20-F24_RECOMMENDATION_LEARNING_EXTENSIONS_WORLD_MODEL_V1.md`](./F20-F24_RECOMMENDATION_LEARNING_EXTENSIONS_WORLD_MODEL_V1.md) — F-20 through F-24: Recommendation Gate, settlement/continuous learning, NCAAF-specific extensions, NFL/NCAAF shared-code extraction rules, and the long-term College Football World Model charter.

## Governing sequence

```text
LAYER 1 — TRUTH & EVIDENCE
F-0 → F-5

LAYER 2 — FOOTBALL STATE
F-6 → F-12

LAYER 3 — FEATURES & TARGETS
F-13 → F-14

LAYER 4 — MODELING & SIMULATION
F-15 → F-17

LAYER 5 — MARKET / RECOMMENDATION / LEARNING
F-18 → F-21

LAYER 6 — NCAAF EXTENSIONS & FUTURE RESEARCH
F-22 → F-24
```

## System-wide locked rules

1. **Full architecture first.** Daily NCAAF is not intentionally built as a disposable MVP.
2. **Predict everything; recommend selectively.** Every eligible supported game/market receives a prediction before the Recommendation Gate acts.
3. **PASS and AVOID are data.** They are stored, settled, calibrated, and evaluated rather than discarded.
4. **Point-in-time correctness is mandatory.** Pregame information is eligible only if `available_at <= prediction_time < kickoff`.
5. **No blanket same-day exclusion.** Legitimately available information may be used through kickoff; later information creates a new immutable snapshot rather than rewriting an old one.
6. **Raw evidence precedes derived truth.** Provider responses are preserved immutably before normalization.
7. **Providers do not define the model.** Canonical contracts and internal IDs are authoritative.
8. **Historical truth and historical knowledge state are different.** Final truth may be known today even when it was unknowable at prediction time.
9. **Football-only and market-aware forecasts remain distinguishable.** Market signal may be modeled, but must not be disguised as independent football signal.
10. **Uncertainty is first-class.** Data, availability, model, and simulation uncertainty must be representable.
11. **Evaluation is chronological.** Primary validation is walk-forward / out-of-time rather than random row splitting.
12. **Promotion requires evidence.** New models become challengers and must earn promotion.
13. **Cross-sport infrastructure belongs in `Daily-Data-Core`.** College-football-native intelligence belongs in `Daily-NCAAF`.
14. **Do not prematurely create a shared NFL/NCAAF package.** Compare both implementations first and extract only semantics proven common.
15. **Architecture history is immutable.** Future changes are versioned rather than silently changing V1.

## Relationship to Daily NFL

Daily NFL is the first production football implementation and provides a useful structural reference. Daily NCAAF intentionally uses the same F-0 through F-24 numbering so equivalent concepts can be compared directly. The two systems are not assumed to be code-identical. College football has materially different competition structure, roster mechanics, eligibility, recruiting, transfer behavior, information quality, schedule heterogeneity, coaching turnover, neutral-site semantics, and market behavior.

After both implementations exist, shared abstractions may be extracted where behavior—not merely naming—is genuinely common.
