# Daily NCAAF — Current Phase

**Current status:** Architecture V1 complete. B.1 complete. B.2-A core complete. B.2-B complete. **B.2-C is active: C1 game/event identity, C2 program/team provider crosswalk, C3 player cross-provider identity and C4 transfer-event reconciliation are COMPLETE/FROZEN; C5 venue/conference/context reconciliation is ACTIVE with C5-A measured/partial and C5-B active.** Phase C production canonical-schema implementation remains intentionally blocked pending the remaining Phase B evidence gates.

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

Current SportsDataverse build documentation states that the CFBD `/games` path is ESPN-origin data redistributed through CFBD, while `espn_cfb_schedules` is ESPN-native. Therefore C1-C5 evidence is described as delivery-path/provider compatibility and coverage reconciliation, **not independent-source corroboration**.

## C1 — Game / event reconciliation — COMPLETE / FROZEN

Freeze:

```text
docs/data/B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md
```

Completed 2024 established 920/920 normalized FBS event overlap, zero unresolved/ambiguous orientations, zero score mismatches and zero team-ID crosswalk conflicts. Provider home/away side is not canonical identity. Kickoff differences remain temporal-semantics evidence.

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

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V18.md
```

User-executed suite:

```text
10 tests
OK
```

Final transfer-event states:

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

All four targeted portal rows had exactly one contextual candidate and matching provider `transferDate` observations.

Cases:

```text
Dillon Gabriel  UCF 2021 -> Oklahoma 2022       TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Dillon Gabriel  Oklahoma 2023 -> Oregon 2024    TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Caleb Downs     Alabama 2023 -> Ohio State 2024 TWO_SIDED_DIRECT_SHARED_ID_BRACKET
Travis Hunter   Jackson State 2022 -> Colorado 2023 PARTIAL_DIRECT_SHARED_ID_BRACKET
```

Hunter remains partial because the ESPN-derived 2022 roster exposes zero Jackson State rows. That source gap is not repaired by name and is not an identity conflict.

Frozen:

```text
portal row != PLAYER identity
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
partial bracket != identity conflict
transferDate != publication time
transferDate != acquired_at
```

## C5 — Venue / conference / context reconciliation — ACTIVE

Governing plan:

```text
docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_PLAN_V1.md
```

### C5-A — native schedule context — MEASURED / PARTIAL

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V19.md
```

User-executed suite:

```text
11 tests
OK
```

Exact-event coverage remained complete from the CFBD side:

```text
2023  910 / 910
2024  920 / 920
2025  934 / 934
```

Critical source-shape result: the selected `espn_cfb_schedules` CSVs do **not** expose event `venue_id` or participant conference/division columns. V1 therefore returned `UNAVAILABLE` for those fields by design; this is not a mismatch.

Measured native schedule context:

```text
venue display text
2023  EXACT 815  MISMATCH 95
2024  EXACT 830  MISMATCH 90
2025  EXACT 827  MISMATCH 107

neutral-site flag
2023  MATCH 907  MISMATCH 3
2024  MATCH 901  MISMATCH 19
2025  MATCH 925  MISMATCH 9

conference-game flag
2023  MATCH 898  MISMATCH 12
2024  MATCH 909  MISMATCH 11
2025  MATCH 933  MISMATCH 1
```

Venue-name differences show sponsor/branding/history drift and do not establish venue identity breaks. Neutral-site differences remain provider observations. Conference-game flag disagreements are retained as special-context semantic observations rather than converted into an undocumented rule.

Locked:

```text
field absent from source artifact != disagreement
UNAVAILABLE != MISMATCH
venue display text != venue identity
neutral-site provider flag != canonical truth by default
conferenceGame != conference_competition semantics by definition
```

### C5-B — team-season context / home-venue anchor — ACTIVE

Plan:

```text
docs/data/B2C_C5_CONTEXT_FOLLOWUP_PLAN_V1.md
```

Tooling:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v2.py
tests/probes/test_cross_provider_context_reconciliation_probe_v2.py
```

C5-B uses documented ESPN-native fields from the published `espn_cfb_teams` season table to evaluate participant division and conference. The published table also carries explicitly backported CFBD fields; those are excluded from second-path evidence.

C5-B compares:

```text
CFBD participant classification
vs ESPN-native team-season division

CFBD participant conference
vs ESPN-native conference aliases
```

For venue IDs, C5-B uses ESPN team-season `venue_id` only as a conservative **home-venue** anchor under non-neutral same-side context. It must never substitute a team home venue for a direct event venue.

Locked distinction:

```text
HOME_VENUE_STINT != GAME_VENUE_OBSERVATION
team-season home venue != event venue by definition
CFBD-backported team fields != ESPN-native evidence
```

## C6 — queued after C5

```text
C6 selected play-level reconciliation
```

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
4. representative game/program/player/context reconciliation supports provider-independent identity contracts;
5. remaining gaps are explicit rather than assumed away;
6. no schema assumes a provider field is complete, unique, canonical, independent, or PIT-safe without evidence.

Production backfill, feature engineering, training, simulation and Recommendation Gate implementation remain intentionally blocked until this gate is met.
