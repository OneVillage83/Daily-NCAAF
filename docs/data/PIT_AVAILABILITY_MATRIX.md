# Daily NCAAF — Historical Point-in-Time Availability Matrix V1

**Phase:** B — Source & Coverage Audit  
**Status:** GOVERNING PIT AUDIT V1; empirical latency/revision probes remain required  
**Audit date:** 2026-08-26

## Purpose

This document defines how candidate source families may enter historical pregame prediction snapshots. It exists to prevent retrospective truth, corrected data, final-season summaries, or modern recomputations from leaking into historical forecasts.

The governing rule remains:

```text
available_at <= prediction_time < kickoff
```

A value being attached to an old season does **not** prove that the value was knowable before an old game.

---

# Canonical temporal vocabulary

Every observation should preserve as many of the following as the source supports:

```text
observed_at     = when the underlying real-world event/state was observed
effective_at    = when the state became effective in football reality
published_at    = when the source publicly released the information
available_at    = earliest defensible time Daily NCAAF could have consumed it
acquired_at     = when our system actually captured the raw evidence
valid_from      = beginning of the state interval represented
valid_to        = end of the state interval represented
superseded_at   = when a later revision replaced the observation
```

These timestamps are different concepts.

Example:

```text
A player enters the portal on Dec 4.
The provider record says transferDate = Dec 4.
Our historical API query in 2026 returns that record.
```

`transferDate` describes the event/effective date. Unless an archived publication timestamp exists, it does not prove exactly when the record became publicly available on Dec 4.

---

# PIT eligibility classes

## PIT-A — Direct contemporaneous evidence

The information was captured or archived with a defensible publication/availability timestamp.

Examples:

- our sportsbook quote snapshot acquired at T-90m;
- our weather forecast payload acquired at T-6h;
- an official availability report with publication time;
- a prospectively captured roster update;
- a provider change-log item with a validated update timestamp.

Eligible when `available_at <= prediction_time`.

## PIT-B — Reconstructable historical state

The value represents historical state, but exact availability requires a documented reconstruction rule or conservative lag.

Examples may include:

- prior-game statistics after the game was finalized;
- season roster snapshots whose original publication time was not retained;
- coach effective state with independent evidence of appointment timing;
- weekly rankings where an official release date can be reconstructed.

PIT-B is usable only after the relevant reconstruction rule is versioned and tested.

## PIT-C — Retrospective truth / retrospective feature

The value is useful for labels, football truth, research, benchmarking, or recomputation but does not represent the historical information state.

Examples:

- final game result;
- actual game participation;
- final historical weather observations when forecasting weather before kickoff;
- a modern algorithm recomputed across old seasons;
- final season totals when predicting games earlier in that season.

PIT-C is not directly eligible for the historical pregame snapshot it describes.

## PIT-U — Unknown

Timestamp or revision semantics are insufficiently understood.

Default rule:

```text
UNKNOWN AVAILABILITY => UNAVAILABLE FOR HISTORICAL PREGAME FEATURES
```

We do not guess an optimistic availability time.

---

# Availability matrix

| Data family | Typical source | Historical PIT class | Governing rule |
|---|---|---:|---|
| scheduled kickoff currently observed | CFBD / schedule provider | A prospectively; B historically | preserve every schedule revision prospectively; historical final schedule is not proof of old scheduled time |
| venue currently observed | CFBD / provider | A prospectively; B historically | venue changes/revisions require temporal state |
| conference membership for active season | CFBD affiliation/effective state | B/A | membership valid for that season may be used once effective; never use future announced realignment before effective season as current membership |
| future conference move | conference-change source | A/B | use as future-state context only if publication/announcement was known by prediction time |
| prior completed game result | CFBD / cfbfastR / NCAA | B/C | result may enter features only after finalization plus dataset-specific availability lag |
| current game's final result | any | C | forbidden in pregame snapshot |
| prior-game PBP | CFBD / cfbfastR | B/C | play events become historical evidence only after they occurred; dataset processing lag must be respected |
| current-game PBP | live source | C for pregame | kickoff boundary forbids any event occurring after game start from pregame models |
| PBP `wallclock` | CFBD/ESPN-derived | timestamp evidence only | event time is not automatically provider publication time |
| prior-game box statistics | CFBD/cfbfastR/NCAA | B | usable after documented finalization/processing lag; corrected versions create revisions |
| season-to-date aggregates recomputed from PIT-safe prior games | Daily NCAAF | A-derived | safe when all source games/fields satisfy cutoff and computation version is known |
| final season aggregates | provider | C for earlier games | never use full-season totals to predict earlier games |
| current roster captured prospectively | CFBD / commercial | A | `acquired_at` provides conservative availability if raw evidence retained |
| historical season roster returned today | CFBD / cfbfastR | B/U | historical season association is not publication history; exact use requires reconstruction/probe |
| actual game roster | cfbfastR / commercial | C/B | actual game roster is truth; cannot assume it was known before kickoff unless published pregame timestamp exists |
| actual snap participation | participant source | C | postgame truth; useful labels/state update for future games after processing lag |
| player transfer record `transferDate` | CFBD | B/U | event/effective date is not automatically publication timestamp |
| transfer destination | CFBD / official report | A/B/U | must not appear before commitment/announcement availability |
| final recruiting class/rating | CFBD | C/B | historical final value may contain later commitments/re-ratings; use snapshot/commit history or conservative class cutoff |
| recruiting commitment observed prospectively | provider/official | A | preserve observation/revision timeline |
| annual team talent composite | CFBD | B/U | capture prospectively; historical release timing must be established before exact-horizon use |
| returning production provider metric | CFBD | B/C | preferably recompute from PIT-safe roster/participation state at a defined preseason cutoff |
| head coach current state | CFBD/official | A/B | active role can enter once appointment/effective state was publicly knowable |
| historical coach tenure effective date | CFBD | B | effective date is useful, but appointment publication timing should be independently reconstructed around transitions |
| interim coach | CFBD/official | A/B | preserve explicit interim stint and public/effective timing |
| OC/DC/play caller | official/commercial/manual | U until source qualified | missing role history cannot be silently inferred from head coach |
| official injury/availability report | conference/program | A if timestamped | source publication time is preferred `available_at` |
| media injury report | credible source/aggregator | A if timestamped | preserve source reliability and exact article/post publication time |
| commercial injury record | SportsDataIO/etc. | A/B | validate provider update timestamp/revision semantics in trial |
| missing injury record | any | not evidence | missing is `UNKNOWN/NO_OBSERVATION`, never `HEALTHY` |
| published depth chart | program/provider | A/B if timestamped | preserve publication date and version; do not equate to actual snaps |
| actual starter/participation | game truth | C | labels future expected-start models; not pregame observation without separate evidence |
| weekly poll/CFP ranking | CFBD/official | B/A | use official release timestamp/date; never backfill a future week's ranking |
| CFBD CORE historical rating | CFBD | C | explicitly retrospective; prohibited as historical pregame feature unless independently reconstructed from PIT inputs |
| other external ratings | CFBD/provider | U/B/C | each rating family requires methodology/publication-era audit; no blanket PIT assumption |
| model rating built internally from eligible prior games | Daily NCAAF | A-derived | safe if training/update uses only information before snapshot and model version is frozen |
| historical open line value | CFBD/cfbfastR | B/U | useful benchmark, but exact quote availability and book timestamp need verification |
| prospectively captured sportsbook quote | Daily-Data-Core | A | direct quote snapshot with `acquired_at`/provider timestamp |
| closing line | Daily-Data-Core/provider | C for earlier snapshots | may enter only a snapshot taken after that quote actually existed; otherwise evaluation truth only |
| historical final weather observation | provider | C for forecast feature | outcome truth, not pregame weather forecast |
| prospectively captured weather forecast | Daily-Data-Core | A | forecast payload timestamp determines availability |
| travel/rest derived from known schedule | Core/NCAAF | A-derived | only schedule revisions known by prediction time may be used |
| final bowl/CFP seed/bracket | CFP official | A after release; C before release | bracket selection may not be backfilled into predictions made before selection release |
| official rules in force | NCAA official | A/B | ruleset becomes season/game context by effective date; future rules not used before effective state unless explicitly modeling future schedule |

---

# Dataset-specific rules

## CFBD CORE

Current CFBD documentation explicitly states that historical CORE ratings are retrospective results produced by the released methodology rather than a record of what the model would have reported at those historical times.

Therefore:

```text
CFBD_CORE_HISTORY -> PIT-C
```

Permitted uses:

- benchmark;
- research target/comparison;
- methodology inspiration;
- retrospective explanatory analysis.

Forbidden use:

- direct historical pregame feature in a walk-forward backtest.

If Daily NCAAF wants a CORE-like metric, compute an internally versioned analogue from PIT-eligible prior-game inputs.

## cfbfastR / SportsDataverse enriched releases

A dataset reprocessed in 2026 for a game played in 2012 is not a 2012 knowledge snapshot.

Fields must be classified individually:

```text
raw event truth          -> usable for future-game state after event/processing lag
modern enrichment        -> recompute ourselves if needed for PIT guarantees
final result/participation -> labels/truth
release metadata         -> not historical event availability
```

The reproducible raw/enriched pipeline is extremely valuable for reconciliation, but release date and event date must never be conflated.

## CFBD historical betting lines

The API exposes open/current-style line fields. Without an exact timestamped quote path, these values are not sufficient to reconstruct arbitrary historical prediction horizons such as T-24h or T-90m.

Use them as:

- historical benchmark lines;
- cross-checks;
- possible opening/closing approximations after validation.

Do not use them as a substitute for `Daily-Data-Core` timestamped quote history.

---

# Conservative availability-lag policy

Daily NCAAF must not globally assume that derived statistics became available at final whistle.

Each source dataset receives an `availability_lag_policy`, for example:

```text
SOURCE_FAMILY
observed completion/event timestamp
+ measured or conservative processing lag
= earliest eligible available_at
```

The lag is determined empirically and versioned.

Until measured:

```text
unknown processing lag -> feature unavailable for snapshots that could be affected
```

We may later establish conservative defaults such as next-day availability for specific historical provider datasets, but those defaults must be evidence-backed rather than invented in Phase B.

---

# Historical reconstruction rules

## Rule 1 — Recompute when possible

Prefer:

```text
PIT-safe prior events
  -> our versioned calculation
```

over:

```text
provider's final historical aggregate
```

for rolling efficiency, returning production, opponent strength and similar state.

## Rule 2 — Preserve revision history

Historical correction:

```text
observation_v1
observation_v2
```

not:

```text
overwrite v1
```

Published predictions retain the version actually used.

## Rule 3 — Unknown means unavailable

No source timestamp + no defensible reconstruction rule = exclude from historical pregame features.

This can reduce training coverage. That is preferable to leakage.

## Rule 4 — Knowledge state and football truth are separate

Example:

```text
Actual starter = Player B
Pregame expected starter probability =
  Player A 65%
  Player B 35%
```

The actual starter is valuable outcome truth. It does not replace the uncertainty that existed before kickoff.

## Rule 5 — Late pregame information is allowed

There is no blanket Saturday exclusion. If a depth, injury, weather, line or roster observation became legitimately available five minutes before kickoff, a prediction snapshot at T-3m may use it.

The only hard boundary is:

```text
prediction_time < official_game_start
```

---

# Availability provenance required on model features

Each material feature snapshot should be traceable to:

```text
feature_value
feature_version
source_observation_ids
max_source_available_at
prediction_time
pit_eligibility_result
coverage_regime
```

For aggregate features, `max_source_available_at` is the latest availability time among contributing evidence.

A feature fails the PIT gate if any nonpermitted source contribution crosses the prediction cutoff.

---

# Empirical Phase B PIT probe

Before Phase B closes, representative source samples must determine:

1. whether provider timestamp fields are event, update, publication or ingestion times;
2. whether old API objects expose only latest corrected state;
3. whether revision history is queryable;
4. how quickly completed games/stat rows appear;
5. how roster/injury/line changes propagate;
6. whether provider IDs remain stable across revisions;
7. whether historical endpoints silently recompute enrichment;
8. whether source payload schemas vary by era;
9. whether time zones are explicit and correct;
10. whether archived provider values can be reproduced from raw evidence.

The resulting evidence will upgrade each matrix entry from `A/B/C/U candidate` to a validated data-contract classification.
