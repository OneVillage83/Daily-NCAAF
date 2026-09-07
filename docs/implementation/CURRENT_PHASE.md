# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity, C2 program/team provider crosswalk, C3 player cross-provider identity, C4 transfer-event reconciliation and C5 venue/conference/context reconciliation are COMPLETE/FROZEN; C6 selected play-level reconciliation is ACTIVE.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

---

# Phase B — Source, Coverage, PIT & Reconciliation Audit

## B.1 — Public Source & Contract Audit — COMPLETE

Provider registry, source coverage matrix, PIT availability matrix, canonical identity rules, ruleset eras and Daily-Data-Core ownership boundaries are documented.

## B.2-A — CFBD games/PBP — CORE COMPLETE

Locked findings include unique sampled game/play IDs, historical `wallclock` coverage boundaries, FBS-involved query semantics, structural PPA nullness, the real Liberty-at-App-State cancellation and current-season revision behavior. Prospective correction/revision timing remains B.2-D.

## B.2-B — CFBD college-native family / identity audit — COMPLETE

Locked:

```text
provider team/player/coach ID != canonical Daily-NCAAF identity
transfer != new player identity
classification change != new player identity
NAME MATCH != IDENTITY MATCH
recruit.committedTo != canonical PLAYER_PROGRAM_STINT
NO TALENT ROW != ZERO TALENT
HTTP 429 != missing data
```

---

# B.2-C — Reconciliation Audit — ACTIVE

## Governing provenance addendum

```text
docs/data/B2C_PROVIDER_PROVENANCE_ADDENDUM_V1.md
```

Current SportsDataverse build documentation states that the CFBD `/games` path is ESPN-origin data redistributed through CFBD, while ESPN-native delivery paths are also available directly. B.2-C evidence is therefore described as delivery-path/provider compatibility and reconciliation evidence, **not independent-source corroboration**.

## C1 — Game / event reconciliation — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md
```

Completed 2024 established 920/920 normalized FBS event overlap, zero unresolved/ambiguous orientations, zero score mismatches and zero team-ID crosswalk conflicts.

Frozen:

```text
provider home/away side != canonical participant identity
scores are compared only after participant alignment
kickoff semantics remain separate from identity
```

## C2 — Program / team provider crosswalk — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C2_PROGRAM_TEAM_CROSSWALK_FREEZE_V1.md
```

Completed 2023-2025:

```text
2023  133 / 133 direct CFBD-ID == ESPN-ID
2024  134 / 134 direct CFBD-ID == ESPN-ID
2025  136 / 136 direct CFBD-ID == ESPN-ID
```

No measured cross-season ID collision occurred. External provider team ID remains separate from canonical `PROGRAM_ID`.

## C3 — Player cross-provider identity — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C3_PLAYER_CROSS_PROVIDER_FREEZE_V1.md
```

Across C3-A + C3-B's 22 FBS slices:

```text
CFBD athlete-ID observations       2745
ESPN athlete-ID observations       2749
shared                             2715
combined weighted CFBD overlap   98.9071%
combined weighted ESPN overlap   98.7632%
```

Frozen:

```text
shared external athlete ID = strong provider-crosswalk identity evidence
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
name inequality != identity break
```

## C4 — Transfer-event reconciliation — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C4_TRANSFER_EVENT_RECONCILIATION_FREEZE_V1.md
```

Final states:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

Frozen:

```text
portal row != PLAYER identity
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
partial bracket != identity conflict
transferDate != publication time
transferDate != acquired_at
```

## C5 — Venue / conference / context reconciliation — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_FREEZE_V1.md
```

Final evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V19.md
docs/data/PROVIDER_PROBE_RESULTS_V20.md
docs/data/PROVIDER_PROBE_RESULTS_V21.md
docs/data/PROVIDER_PROBE_RESULTS_V22.md
```

C5-A proved the selected ESPN-native schedule assets do not expose direct event `venue_id` or participant conference/division columns. Missing fields remained `UNAVAILABLE`, not mismatches.

C5-B used ESPN-native team-season metadata and measured complete participant team-ID and division agreement across completed 2023-2025, with no referenced team metadata gaps. It also demonstrated that team-season home-venue metadata is not safe event-venue truth.

C5-C/V3 retained explicit provider naming equivalence for the American Athletic family without introducing fuzzy matching.

C5-D/V4 completed the exhaustive residual classification. The corrected user-executed suite passed:

```text
10 tests
OK
```

Final residual conference classes:

```text
CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       37
TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
UNCLASSIFIED                                    0
```

Exact signatures:

```text
Big South       vs ESPN OVC umbrella   1
Big South-OVC   vs ESPN OVC umbrella  22
OVC-Big South   vs ESPN OVC umbrella  14
UAC             vs ESPN Southland      1
```

C5 freeze gate:

```text
external team-ID conflicts             0
division conflicts                     0
missing referenced team metadata       0
unclassified conference residuals      0
```

Frozen:

```text
FIELD ABSENT != MISMATCH
UNAVAILABLE != CONTRADICTORY DATA
provider display label != canonical identity
venue display text != venue identity
TEAM_SEASON_HOME_VENUE_OBSERVATION != GAME_VENUE_OBSERVATION
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
provider neutral-site flag != canonical truth by default
conferenceGame != conference_competition semantics by definition
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
TEAM-SEASON CONFERENCE METADATA != guaranteed historical affiliation truth
provider conference ID != canonical CONFERENCE_ID
provider venue ID != canonical VENUE_ID
```

## C6 — Selected play-level reconciliation — ACTIVE

Plan:

```text
docs/data/B2C_C6_SELECTED_PLAY_RECONCILIATION_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_play_reconciliation_probe.py
tests/probes/test_cross_provider_play_reconciliation_probe.py
```

Contract:

```text
DAILY_NCAAF_PHASE_B2C_SELECTED_PLAY_RECONCILIATION_V1
```

C6-A compares a deterministic set of already-reconciled event IDs across 2023-2025 using CFBD historical `/plays` and ESPN site-v2 summary play-by-play.

The first identity question is exact play-ID compatibility:

```text
exact PLAY_ID equality before semantic comparison
```

Only exact shared play IDs are compared on:

```text
period
clock seconds
down
distance
yards to goal
scoring flag
play type text
play text
```

Provider-only play rows remain explicit. C6-A does not force-match by row order, clock or text.

If exact play-ID overlap is insufficient, C6 proceeds to a bounded C6-B composite-alignment study rather than weakening the identity contract.

Cross-delivery matching never makes a historical source PIT-safe by itself.

---

## B.2-D — Prospective live timestamp/revision capture — STILL REQUIRED

Required repeated evidence:

```text
provider timestamp(s)
our acquired_at
payload/record hash
revision delta
correction time
```

The 2026 source-state lag observed during C1 supports this gate but does not replace prospective repeated live capture.

## B.2-E — Availability-source trial — QUEUED

Evaluate official conference/program feeds plus commercial trials against timestamp, revision, identity, latency and missing-report criteria because the public ESPN-derived injury family produced zero observations across completed 2024.

---

# Phase B -> Phase C transition rule

Production canonical schema remains blocked until:

1. major F-0 through F-14 source families have empirical coverage evidence where access permits;
2. inaccessible/commercial families are explicitly trial/credential-gated;
3. major PIT/revision semantics have validated classifications or conservative exclusions;
4. representative game/program/player/context/play reconciliation supports provider-independent identity contracts;
5. remaining gaps are explicit rather than assumed away;
6. no schema assumes a provider field is complete, unique, canonical, independent, or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
