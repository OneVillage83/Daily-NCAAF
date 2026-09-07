# Daily NCAAF — Provider Probe Results V1

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** INITIAL PUBLIC-REPOSITORY PROBE COMPLETE; authenticated/commercial endpoint probes remain  
**Probe date:** 2026-08-26

## Purpose

Phase B.1 established provider capabilities from public documentation. This file begins B.2 by inspecting actual source-code/schema artifacts where public access permits, rather than relying only on provider summaries.

This is intentionally a **probe**, not production ingestion code.

---

# Probe P-001 — SportsDataverse/cfbfastR dataset registry and schema

## Source inspected

- `sportsdataverse/cfbfastR-cfb-data/DATASETS.md`
- `sportsdataverse/cfbfastR-cfb-data/python/cfb_data_build/config.py`
- `sportsdataverse/cfbfastR-cfb-data/R/espn_cfb_14_injuries_creation.R`
- `sportsdataverse/cfbfastR-cfb-data/docs/models/era_model_refresh.md`
- `sportsdataverse/cfbfastR-cfb-raw/README.md`

## Result: broad dataset family is real and machine-defined

The current dataset registry directly defines released datasets including:

```text
play_by_play
team_box
player_box
play_participants
drives
game_rosters
rosters
betting
schedules
linescores
power_index
injuries
advanced team/player/unit tables
```

The current schema document describes `play_by_play` as 380 columns and identifies `play_participants`, `game_rosters`, `rosters`, `betting`, `schedules`, `injuries`, and multiple advanced tables as separate release artifacts.

**Audit conclusion:** upgrade this family from documentation-only discovery to `PUBLIC_ARTIFACT_VERIFIED` for dataset existence/schema architecture.

Exact row completeness by season remains unmeasured.

---

# Probe P-002 — Raw vs enriched lineage is explicit

The raw repository documents a two-stage structure:

```text
ESPN summary
  -> raw/{game_id}.json
  -> final/{game_id}.json
       enriched with EPA/WPA/QBR,
       advanced box score,
       participants,
       game rosters,
       betting,
       recent FPI, etc.
```

The repository can rebuild `final` offline from retained raw JSON after a pipeline/model change.

## PIT consequence

This is excellent for reproducibility but proves that `final` is **not immutable contemporaneous historical knowledge state**.

A 2010 game can receive newly recomputed enrichment in 2026.

Therefore Daily NCAAF classification is:

```text
raw event fields          -> historical football evidence
final enrichment          -> derived/recomputed evidence
release parquet           -> analysis artifact
```

For model features we should prefer our own versioned recomputation from raw/PIT-eligible prior-game truth rather than blindly copying modern enrichment into old prediction snapshots.

---

# Probe P-003 — Historical PBP era verified at repository level

The current cfbfastR era-refresh documentation states that in June 2026 the full CFB PBP corpus covering **2004-2025** was reprocessed, approximately **18.6k games**.

The raw repo's documented full-backfill command begins at 2004.

## Conclusion

Use **2004** as the first empirical PBP coverage boundary to test, not yet as a guaranteed complete Daily NCAAF training start year.

Why not lock it yet?

- schedule/game completeness still needs count reconciliation;
- field completeness varies by era;
- pre-2014 player identity required later reconstruction improvements;
- advanced/external fields have later coverage regimes.

---

# Probe P-004 — Modern reprocessing materially changes old-game fields

The 2026 era-refresh documentation records two important retroactive changes across the 2004-2025 corpus:

1. betting spread/total inputs were replaced with a multi-book consensus history for 2006-2025;
2. pre-2014 player-name extraction and team-aware player-ID attribution were improved.

The report also says models were retrained on the refreshed corpus.

## PIT consequence

This is direct evidence that:

```text
historical row today != historical feature snapshot then
```

Player IDs, model outputs and betting-derived enrichment can improve years later.

Daily NCAAF must preserve:

```text
raw_source_version
normalization_version
enrichment_version
model_version
```

and must not treat a current release as the immutable historical publication state.

---

# Probe P-005 — PBP schema contains explicit look-ahead columns

The current `play_by_play` schema includes fields such as:

```text
lead_text
lead_start_team
lead_start_yardsToEndzone
lead_start_down
lead_start_distance
lead_scoringPlay
```

These explicitly describe the **next play**.

## Leakage consequence

For a play-level next-state model, these columns are target/future leakage and are prohibited as predictor inputs.

For a future-game pregame model, completed prior-game information may be summarized after the prior game is legitimately available, but the presence of these fields still demonstrates why Daily NCAAF cannot whitelist an entire provider table as “features.”

We require a **field-level feature contract**.

The schema also contains modern derived columns such as EPA/WPA/model inputs; those require independent provenance/version review.

---

# Probe P-006 — PBP timestamp semantics are richer but still not sufficient alone

The cfbfastR PBP schema exposes both:

```text
modified  = ESPN last-modified timestamp for the play record
wallclock = timestamp the play occurred
```

These are useful provenance signals.

However:

- `wallclock` is event time, not necessarily API-publication time;
- `modified` can reflect a later correction and therefore cannot automatically be used as the original availability timestamp;
- release-file creation time is not event availability.

## Required future probe

Capture a live/current game prospectively and compare:

```text
play wallclock
provider modified
our HTTP acquired_at
next observed revision
```

before assigning a production live-PIT contract.

---

# Probe P-007 — Injury dataset exists but is explicitly sparse

The current cfbfastR injury-builder source contains the following implementation comment in substance:

> the ESPN CFB injury block is frequently empty; when empty the builder returns a zero-row frame.

The builder merely flattens the per-team/per-athlete injury block when ESPN populates it.

## Conclusion

This confirms a critical Phase B finding:

```text
injury dataset exists
!=
uniform national injury coverage
```

Daily NCAAF therefore **must not** use:

```text
no injury row -> player healthy
```

The correct state is:

```text
NO_OBSERVATION / UNKNOWN
```

unless stronger evidence exists.

This increases the priority of official conference/program report adapters and the SportsDataIO/Sportradar trials.

---

# Probe P-008 — Recent-only auxiliary coverage is explicit

The cfbfastR raw repository documents:

```text
EXTRAS_MIN_SEASON = 2015
```

for recent-season FPI/full-event-odds extras because those endpoints do not return older data in the same way.

It also documents that CFB officials were not available from the probed ESPN paths and CFB prop-bet endpoints returned unavailable/404 behavior.

## Conclusion

A 2004-2025 PBP corpus does not imply 2004-2025 coverage for every adjacent dataset.

Daily NCAAF requires independent coverage regimes by family/field.

---

# Probe P-009 — Recruit source floor is itself coverage-quality dependent

The raw repository documents a 247 recruiting backfill floor of **2002**, with an explicit rationale that ratings collapse in completeness before that point.

## Conclusion

This is another useful example of why “endpoint accepts old year” is weaker than “old-year data is model-quality complete.”

The recruiting probe should measure:

```text
recruits per class
rated percentage
stars/rating null rate
team linkage
athlete-id linkage
position coverage
```

by class before setting an early-season player-prior era.

---

# Probe P-010 — Season-level summary tables are post-season aggregates

The current cfbfastR schema explicitly distinguishes several season-level summary datasets produced by aggregating a **full season** of enriched PBP.

Examples include team summaries and passing/rushing/receiving summaries.

## PIT consequence

Full-season summary tables are prohibited as direct predictors for games earlier in the same season.

If we want analogous features, Daily NCAAF computes rolling season-to-date values from prior eligible games at the prediction snapshot.

---

# Probe P-011 — CFBD authenticated endpoint requirement

Current CFBD documentation requires a Bearer API key for data calls such as `/games`, `/plays`, `/players`, and related endpoint families.

No credential is stored in this repository, and Phase B must not request or commit secrets.

## Conclusion

Row-level CFBD empirical probes are **credential-gated**, not “failed” or assumed complete.

The later probe implementation should read:

```text
CFBD_API_KEY
```

from environment configuration only.

It should produce local/ignored raw evidence plus checked-in aggregate probe reports that contain no secret.

---

# First empirical findings summary

| Finding | Result | Architectural effect |
|---|---|---|
| cfbfastR datasets exist as machine-defined registry | VERIFIED | valid reconciliation candidate |
| broad PBP corpus | 2004-2025 repo-documented | candidate historical baseline |
| raw/final distinction | VERIFIED | preserve raw vs enrichment provenance |
| historical reprocessing | VERIFIED | current release is not historical knowledge snapshot |
| next-play `lead_*` fields | VERIFIED | field-level leakage controls mandatory |
| event vs modified timestamps | VERIFIED | timestamp semantic testing required |
| CFB injuries frequently empty | VERIFIED in builder source | missing != healthy; multi-source availability required |
| FPI/full event-odds extras | recent-only; gated at 2015 in raw pipeline | field-specific coverage regimes required |
| ESPN CFB officials/propbets via that pipeline | unavailable in documented probe | do not build dependency on them |
| recruit backfill floor | 2002 with pre-floor completeness collapse noted | recruiting era requires quality probe |
| full-season summaries | explicitly full-season derived | forbidden for earlier same-season snapshots |
| CFBD row probe | Bearer-key gated | next probe uses env secret, never repo secret |

---

# B.2 next probe sequence

## B.2.1 — Public artifact probes — STARTED / initial pass complete

Next inspect downloadable/release manifests and, where practical, representative public season artifacts for:

```text
2004
2010
2014
2018
2020
2023
2024
2025
```

Measure table presence, schemas, game counts and null patterns without treating public release enrichment as PIT state.

## B.2.2 — CFBD authenticated read-only probe — CREDENTIAL-GATED

Once a local environment has `CFBD_API_KEY`, run a small read-only probe across the representative season/game strata defined in `SOURCE_COVERAGE_MATRIX.md`.

No production ingestion yet.

## B.2.3 — Live timestamp probe — SEASON/ACCESS DEPENDENT

Capture prospective schedule/roster/play revisions with `acquired_at` to understand provider latency and correction behavior.

## B.2.4 — Commercial provider trials — ACCESS/COST GATED

Evaluate SportsDataIO and Sportradar only after defining the exact gap questions they must answer:

- historical injury revision depth;
- current injury latency;
- game-roster publication timing;
- change-log behavior;
- cross-provider player ID quality;
- commercial storage/redistribution constraints.

---

# Phase B status after this probe

Phase B remains **ACTIVE**.

We now have enough evidence to reject several dangerous shortcuts, but not enough row-level cross-provider measurements to lock the Phase C canonical database contracts.

The project should continue B.2 rather than advance prematurely.
