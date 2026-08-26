# Daily NCAAF — Source Coverage Matrix V1

**Phase:** B — Source & Coverage Audit  
**Status:** DOCUMENTATION-VERIFIED MATRIX; empirical endpoint probes still required  
**Audit date:** 2026-08-26

## Purpose

This document maps the data families required by Daily NCAAF F-0 through F-14 to the sources that can currently support them. It distinguishes documented capability from empirically validated season-by-season completeness.

A provider appearing in this matrix does **not** mean that all seasons, teams, fields, or revisions are complete. Exact usable coverage is established only after the Phase B empirical probe.

## Coverage labels

- **DOC-VERIFIED** — current provider documentation/repository explicitly exposes the family.
- **PARTIAL** — useful coverage exists but it does not satisfy the complete canonical requirement.
- **RECONCILIATION** — useful as a second source or truth check rather than sole source.
- **CORE** — owned by `Daily-Data-Core`.
- **GAP** — no satisfactory production-grade source has yet been established.
- **TRIAL** — commercial/provider trial required.
- **PROBE** — exact seasons/completeness/timestamps still require empirical measurement.

---

# Coverage matrix

| Data family | CFBD | SportsDataverse / cfbfastR | NCAA / CFP official | Commercial / official reports | Daily-Data-Core | Current conclusion |
|---|---|---|---|---|---|---|
| competition / season / week | DOC-VERIFIED | DOC-VERIFIED | RECONCILIATION | — | — | supported |
| game schedule / game identity | DOC-VERIFIED | DOC-VERIFIED | RECONCILIATION | Sportradar TRIAL | — | supported; revision history PROBE |
| final result | DOC-VERIFIED | DOC-VERIFIED | official RECONCILIATION | Sportradar TRIAL | settlement CORE | strong |
| FBS/FCS classification | DOC-VERIFIED | derivable | official reference | — | — | supported |
| historical conference affiliation | DOC-VERIFIED | PARTIAL/derivable | official reference | — | — | strong; time-version canonical state required |
| conference changes / effective year | DOC-VERIFIED | PARTIAL | official reference | — | — | supported |
| program metadata | DOC-VERIFIED | DOC-VERIFIED | official RECONCILIATION | — | — | strong |
| venue / stadium | DOC-VERIFIED | PARTIAL | official reference | Sportradar TRIAL | venue primitives CORE | supported; historical venue stints PROBE |
| venue lat/long/time zone/elevation/surface | DOC-VERIFIED | PARTIAL | — | — | geospatial CORE | useful seed; historical change coverage PROBE |
| play-by-play | DOC-VERIFIED historical + live | DOC-VERIFIED 2004-2025 corpus | — | Sportradar TRIAL | — | strong historical foundation |
| drives | DOC-VERIFIED | DOC-VERIFIED | — | Sportradar TRIAL | — | supported |
| team box statistics | DOC-VERIFIED | DOC-VERIFIED | official RECONCILIATION | Sportradar TRIAL | — | strong |
| player box statistics | DOC-VERIFIED | DOC-VERIFIED | official RECONCILIATION | Sportradar TRIAL | — | strong, identity PROBE |
| play participants | player/play stat associations PARTIAL | DOC-VERIFIED play participants | — | Sportradar TRIAL | — | useful but snap completeness must be measured |
| snap counts / exact participation | PARTIAL / not uniform in public docs | PARTIAL via participants/game rosters | — | commercial TRIAL | — | GAP/PARTIAL; high-value research area |
| season rosters | DOC-VERIFIED | DOC-VERIFIED | RECONCILIATION | Sportradar TRIAL | — | supported; exact historical completeness PROBE |
| game rosters | not established as complete national family | DOC-VERIFIED | — | Sportradar game roster TRIAL | — | PARTIAL; valuable for availability reconstruction |
| canonical player search/team stints | DOC-VERIFIED | PARTIAL | — | — | — | strong seed, cross-provider linking required |
| recruiting player rankings | DOC-VERIFIED | via CFBD wrappers/derivations | — | — | — | supported; historical revision PIT issue |
| recruiting team rankings | DOC-VERIFIED | via CFBD wrappers/derivations | — | — | — | supported |
| team talent composite | DOC-VERIFIED | — | — | — | — | supported as annual prior; snapshot timing PROBE |
| transfer portal | DOC-VERIFIED | via CFBD ecosystem/other pipelines | — | possible commercial | — | supported event family; publication-time history PROBE |
| returning production | DOC-VERIFIED | derivable | — | — | — | supported/derivable; recomputation preferred for PIT |
| eligibility | portal eligibility PARTIAL | PARTIAL | official rules/reference | commercial/official sources PARTIAL | — | GAP/PARTIAL |
| redshirt state | not established as complete national historical family | not established complete | official rules only | possible commercial/program sources | — | GAP |
| NFL draft departures | DOC-VERIFIED draft results | derivable | official NFL/NCAA reference possible | — | — | supported departure truth |
| head coach identity/history | DOC-VERIFIED | PARTIAL | official reference | Sportradar possible | — | strong |
| interim head coach state | DOC-VERIFIED tenure field | PARTIAL | official reference | — | — | supported |
| OC / DC identity history | not equivalent to head-coach coverage | not uniform | program/reference manual research | commercial/official research | — | GAP |
| play-caller history | not established | not uniform | program/reference manual research | commercial/official research | — | GAP |
| injuries / availability reports | no uniform public national endpoint established | injuries dataset exists from ESPN-derived pipeline | conference/program official reports | SportsDataIO TRIAL; Sportradar TRIAL | — | major PARTIAL/GAP; multi-source architecture required |
| published depth charts | no uniform national family established | not a reliable complete national family | program sources | SportsDataIO explicitly does not provide college depth charts | — | major GAP |
| expected starter probability | derived only | derived only | — | derived from observations | — | model output, not raw provider field |
| polls / rankings | DOC-VERIFIED | PARTIAL | official CFP/AP reference as applicable | — | — | supported |
| SP+ / SRS / Elo / FPI / CORE | DOC-VERIFIED | some recent ratings | — | — | — | benchmark/research; PIT varies by rating |
| opponent strength / SOS | derivable + rating endpoints | derivable | — | — | — | must be recomputed from PIT-safe state for production features |
| advanced efficiency / PPA / WP | DOC-VERIFIED | enriched datasets | — | Sportradar possible | — | useful research, but algorithm/version lineage required |
| historical betting lines | DOC-VERIFIED open/current/final-style fields | normalized betting | — | commercial odds candidates | production odds CORE | benchmark supported; exact timestamp history incomplete |
| timestamped sportsbook quote history | insufficient as sole exact-horizon history | not complete national timestamped book tape | — | odds provider via Core | CORE | must be solved in Daily-Data-Core |
| historical final weather | game-weather fields available | PARTIAL | — | commercial possible | — | useful truth only; not forecast PIT state |
| forecast snapshots | not guaranteed historical forecast tape | — | NWS reference possible | weather provider | CORE | Daily-Data-Core responsibility |
| travel distance / time zones | inputs available | inputs derivable | — | — | CORE primitives | derive canonically |
| rest / bye / schedule sequence | schedule-derived | schedule-derived | — | — | CORE primitives | supported |
| official playing rules | — | — | NCAA official | — | — | authoritative source |
| CFP format / postseason structure | game metadata partial | schedule-derived | CFP official | — | — | authoritative official reference |
| corrections / revision events | endpoint-specific, PROBE | raw/enriched regeneration history useful | official corrections possible | change-log candidates | generic revisions CORE | requires explicit canonical revision model |

---

# Historical coverage landmarks currently verified from documentation

These are **landmarks**, not promises of complete coverage.

## 2004-2025 — cfbfastR PBP corpus

The current SportsDataverse/cfbfastR data pipeline documents a full PBP reprocessing pass covering 2004 through 2025, approximately 18.6k games. This establishes a strong second historical PBP corpus for validation and reconciliation.

It does **not** prove every enriched field existed historically at prediction time.

## Recruiting data

CFBD recruiting endpoints expose historical recruiting players, team rankings and position-group aggregates. Some endpoint defaults/parameters extend to older classes, but completeness by class, recruit type, team and provider linkage must be empirically measured before we lock a minimum training era.

## 2016+ — CFBD CORE public history

CFBD documents public CORE historical ratings beginning in 2016. Those historical ratings are explicitly retrospective and therefore are a coverage landmark for benchmark/research use, not a PIT-safe pregame feature era.

## 2018+ — SportsDataIO injury field metadata

The current SportsDataIO NCAA Football data dictionary marks `InjuryStatus` as available from 2018. This is sufficient to justify a trial query for historical injury coverage, but not sufficient to assume complete, revision-preserving injury history from 2018 onward.

## Recent-only enrichment families

The current cfbfastR raw pipeline gates some FPI/full-event-odds extras to more recent seasons. Coverage-era flags must therefore exist even when the broader PBP corpus reaches 2004.

---

# Coverage regimes must be explicit

Daily NCAAF must never pretend all seasons have the same information environment.

A future canonical table should support something conceptually equivalent to:

```text
DATA_COVERAGE_REGIME

coverage_regime_id
family
provider
start_date
end_date
classification
field_set_version
completeness_grade
pit_grade
notes
```

Feature contracts then declare the minimum acceptable coverage regime.

Example:

```text
feature = QB_PRESSURE_RATE
requires participation/pressure fields
coverage regime = MODERN_PBP_ENRICHED
```

A model trained across 2004-2026 cannot silently fill early eras with modern-only fields.

---

# Critical unresolved gaps

## G-01 — National historical injury/availability timeline

No currently verified open/public source provides a uniform, high-confidence, timestamped national historical injury-report tape covering the desired modeling horizon.

Strategy:

1. official conference/program reports when available;
2. commercial injury feed trial;
3. SportsDataverse/ESPN-derived injury records as reconciliation/research;
4. game roster/participation inference;
5. explicit availability uncertainty and source reliability;
6. never infer `HEALTHY` merely from missing injury evidence.

## G-02 — Published depth-chart history

No satisfactory uniform national historical depth-chart source has been established.

Canonical architecture therefore distinguishes:

```text
PUBLISHED_DEPTH_CHART_OBSERVATION
EXPECTED_STARTER_PROBABILITY
ACTUAL_PARTICIPATION
```

The second is modeled state; the third is retrospective truth.

## G-03 — Coordinator / play-caller history

Head-coach history is materially stronger than OC/DC/play-caller history in the currently verified source stack. Phase B must preserve this as a separate research/acquisition problem rather than silently copying the head coach across all scheme roles.

## G-04 — Exact historical market tape

CFBD/cfbfastR are valuable benchmark sources, but they do not replace a timestamped, sportsbook-specific quote history suitable for exact T-24h/T-6h/T-90m backtesting. This belongs in `Daily-Data-Core`.

## G-05 — Eligibility / redshirt history

Transfer eligibility exists in some portal records, but a complete historical national redshirt/eligibility-state ledger is not yet established.

---

# Empirical coverage probe — required before Phase B closes

The next subphase must query representative endpoint/provider samples and record actual measurements.

## Probe seasons

At minimum:

```text
2004
2006
2010
2014
2015
2016
2018
2019
2020
2021
2023
2024
2025
2026
```

This spans the earliest cfbfastR PBP era, CFP transition, modern enrichment, COVID-era irregularities, major timing-rule changes, and current live-state behavior.

## Probe program/game strata

At minimum include:

- high-resource FBS programs;
- Group of Five programs;
- independent programs;
- FCS programs;
- FBS-vs-FCS games;
- neutral-site games;
- conference championships;
- bowls;
- CFP games;
- programs that changed conferences;
- transferred players with multiple school stints;
- coaching transitions/interim coaches;
- games with known injury/availability uncertainty.

## Measurements per endpoint/dataset

Record:

```text
row_count
expected_entity_count
missing_entity_count
field_null_rate
key_null_rate
duplicate_key_rate
provider_id_stability
cross-provider_match_rate
classification_coverage
season_coverage
revision_behavior
timestamp_fields
timestamp_semantics
latency_if_live
correction_behavior
schema_hash
raw_checksum
```

## Completion criteria

The matrix can move from `DOC-VERIFIED` to `EMPIRICALLY-VERIFIED` only after probe evidence exists in the repository.

---

# Schema implications already justified by Phase B evidence

Without designing the full production schema yet, the coverage audit already requires these properties:

1. provider observations remain separate from canonical entities;
2. every canonical entity supports provider crosswalks;
3. conference/classification/program/roster/coach state is time-versioned;
4. missing data carries structured missingness/source-quality semantics;
5. coverage regime and PIT grade are queryable;
6. injury/depth state is observational/probabilistic, not a single truth column;
7. historical data supports revisions rather than overwrite;
8. feature computation can declare minimum coverage requirements;
9. market/weather production state is consumed from `Daily-Data-Core`;
10. provider-specific enriched metrics never become opaque canonical truth.

These requirements are evidence-driven constraints for Phase C, not a premature provider-shaped database design.
