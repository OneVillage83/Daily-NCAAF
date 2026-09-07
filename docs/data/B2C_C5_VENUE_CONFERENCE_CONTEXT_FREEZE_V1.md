# B.2-C C5 — Venue / Conference / Context Reconciliation Freeze V1

Status: **COMPLETE / FROZEN**  
Date: 2026-09-07

## Scope

This freeze closes B.2-C C5 for the measured 2023-2025 completed-season delivery-path reconciliation window.

C5 combined four bounded passes:

```text
C5-A  native schedule context                 MEASURED / PARTIAL
C5-B  ESPN-native team-season context         MEASURED
C5-C  explicit American naming equivalence    MEASURED
C5-D  exhaustive residual classification      COMPLETE
```

This is a provider/delivery-path compatibility freeze, not independent-source corroboration. The governing provenance addendum remains authoritative.

## Freeze evidence

Primary evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V19.md
docs/data/PROVIDER_PROBE_RESULTS_V20.md
docs/data/PROVIDER_PROBE_RESULTS_V21.md
docs/data/PROVIDER_PROBE_RESULTS_V22.md
```

Final V4 validation:

```text
10 tests
OK
```

Completed-season game-ID coverage:

```text
2023  910 / 910
2024  920 / 920
2025  934 / 934
```

All aligned participant external team IDs and division labels matched. No referenced team metadata was missing.

Final residual conference classification:

```text
CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       37
TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
UNCLASSIFIED                                    0
```

## Frozen identity and context rules

### 1. Provider context remains observational

```text
provider field != canonical truth merely because it is populated
provider display label != canonical identity
provider conference ID != canonical CONFERENCE_ID
provider venue ID != canonical VENUE_ID
```

### 2. Missing fields remain missing

The ESPN-native schedule artifacts used in C5-A do not expose event `venue_id` or participant conference/division columns.

```text
FIELD ABSENT != MISMATCH
UNAVAILABLE != CONTRADICTORY DATA
```

### 3. Venue name is not venue identity

Sponsor changes, historical names, abbreviations and stale team-season home-venue metadata were observed.

```text
venue display text != venue identity
TEAM_SEASON_HOME_VENUE_OBSERVATION != GAME_VENUE_OBSERVATION
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
```

A team-season home venue may be used as contextual evidence only. It must never silently replace the direct event venue.

### 4. Neutral-site and conference-game flags are source semantics

```text
provider neutral-site flag != canonical truth by default
conferenceGame != conference_competition semantics by definition
```

Disagreements are retained with provider, source artifact and acquisition provenance.

### 5. Conference aliases must be explicit and evidence-backed

Allowed measured naming-equivalence groups at this freeze:

```text
American Athletic
American Conference
American
```

and:

```text
Coastal Athletic
Coastal Athletic Association
CAA
```

No fuzzy string matching is authorized by this freeze.

### 6. Conference association is not the same as membership

The Big South/OVC residuals demonstrate that a joint football association can be represented differently from underlying member-conference metadata.

```text
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
```

Production schema must be able to represent both if both concepts are needed.

### 7. Team-season conference metadata is not guaranteed historical truth

The measured 2023 Stephen F. Austin `UAC` versus ESPN-native `Southland` difference is retained as a temporal-affiliation conflict candidate.

```text
TEAM-SEASON CONFERENCE METADATA
!=
guaranteed historical CONFERENCE_AFFILIATION_STINT truth
```

Canonical affiliation requires a time-bounded stint plus evidence provenance. Later/current metadata cannot silently rewrite earlier seasons.

## Canonical production implications

Phase C should preserve at least these concepts distinctly:

```text
PROGRAM
CONFERENCE
CONFERENCE_AFFILIATION_STINT
CLASSIFICATION_STINT
VENUE
HOME_VENUE_STINT
GAME_VENUE_OBSERVATION
GAME_CONTEXT_OBSERVATION
PROVIDER_CONTEXT_OBSERVATION
```

Each provider observation must retain source and acquisition lineage.

## Change control

This V1 freeze may be changed only by additive versioned evidence.

New provider behavior may add:

```text
new explicit alias equivalence
new association semantic
new temporal-conflict class
new venue-context rule
```

but must not silently rewrite the historical meaning of this freeze.

## Exit decision

C5 freeze criteria passed:

```text
exact game identity preserved                    yes
external participant identity conflict-free      yes
division/classification conflict-free             yes
missing referenced metadata                       0
unclassified residual conference signatures       0
venue/context limitations explicitly represented  yes
```

**B.2-C C5 is COMPLETE / FROZEN.**

Next gate:

```text
B.2-C C6 — selected play-level reconciliation
```
