# Daily NCAAF — B.2-C Cross-Provider Reconciliation Plan V1

**Phase:** B.2-C — CFBD <-> ESPN/cfbfastR Reconciliation  
**Status:** ACTIVE  
**Precondition:** B.2-B CFBD college-native coverage/identity audit complete

---

## 1. Objective

B.2-C measures how independently sourced CFBD and ESPN/cfbfastR observations map onto the same real football entities/events.

The goal is **not** to choose one provider as canonical truth.

The goal is to establish provider-independent reconciliation contracts for:

```text
game/event identity
program/team identity
player identity
transfer continuity
venue/context agreement
selected play-level agreement
```

Every reconciliation result must retain its source evidence and ambiguity state.

---

## 2. Source roles

### CFBD

Use authenticated read-only endpoints already measured in B.2-A/B.2-B.

For the first event pass:

```text
GET /games?year=<season>&seasonType=both&classification=fbs
```

Important previously locked scope rule:

```text
classification=fbs -> FBS-involved event universe
```

not strict FBS-vs-FBS only.

### SportsDataverse / cfbfastR

Use the public `espn_cfb_schedules` release from `sportsdataverse/sportsdataverse-data`.

Current public schedule assets are season-specific and expose ESPN event `game_id` as the schedule primary key.

The first reconciliation harness records the public asset URL and SHA-256 of the bytes it actually used.

Current public-data architecture was rechecked on 2026-08-31 against:

```text
sportsdataverse/cfbfastR-cfb-data
sportsdataverse/sportsdataverse-data release tag espn_cfb_schedules
```

Public release publication/update time is **not** historical pregame availability time.

---

## 3. B.2-C execution order

### C1 — Game/event identity and universe reconciliation — ACTIVE FIRST

Target initial seasons:

```text
2024
2026
```

Why these two first:

- 2024 is completed and was deeply measured in both provider families;
- 2026 provides current-state/live-era behavior and catches revision/state differences;
- the 2024 Liberty-at-App-State cancellation is a useful lifecycle edge case.

Measure:

1. CFBD game-ID uniqueness;
2. ESPN/cfbfastR `game_id` uniqueness;
3. exact numeric/string ID overlap;
4. CFBD FBS-involved events missing from ESPN schedule;
5. ESPN schedule events outside the CFBD FBS-involved response;
6. matched-event home/away team-name agreement;
7. week agreement;
8. kickoff/start-time agreement where parseable;
9. score/completion/lifecycle differences where fields exist;
10. whether provider IDs can be treated as direct crosswalk evidence for games.

### Critical universe rule

Raw season totals are not directly comparable unless event universes are normalized.

Therefore C1 reports both:

```text
CFBD -> ESPN exact-ID coverage
```

and:

```text
ESPN extras relative to CFBD FBS-involved query
```

without automatically declaring ESPN extras to be duplicates or CFBD omissions.

If ESPN classification/division fields are available, the harness also computes an FBS-involved ESPN subset. Otherwise the extra set remains explicitly `UNIVERSE_UNNORMALIZED`.

---

### C2 — Team/program crosswalk reconciliation

After game IDs are measured, derive provider-team pairs from matched events.

Measure:

```text
CFBD team id/name
<-> ESPN team id/name
```

across seasons.

Required states:

```text
DIRECT_EVENT_SUPPORTED_CROSSWALK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

Never create a permanent program crosswalk from one name-only observation.

Crosswalk evidence must tolerate:

- historical renames;
- abbreviations;
- punctuation;
- directional names;
- provider aliases;
- classification changes.

Canonical Daily-NCAAF `PROGRAM_ID` remains provider-independent.

---

### C3 — Player cross-provider reconciliation

Use the B.2-B positive/hard identity cases as anchors.

Initial player anchors:

```text
Jalen Milroe
Dillon Gabriel
Travis Hunter
Caleb Downs
```

Compare CFBD provider athlete IDs against ESPN/cfbfastR season/game-roster athlete IDs and metadata.

Measure stability through:

- same-program seasons;
- FBS transfers;
- FCS -> FBS movement;
- jersey/position changes.

Names discover candidates only.

---

### C4 — Transfer continuity

For known transfer cases, reconcile:

```text
CFBD stable roster athlete identity
CFBD portal observation
ESPN/cfbfastR origin roster evidence
ESPN/cfbfastR destination roster evidence
```

The portal row itself remains an observation, not canonical player identity.

---

### C5 — Venue/conference/context agreement

On matched games, compare:

- venue identity/name;
- neutral-site state;
- conference-game state;
- home/away conference context;
- season/week/type.

Differences become explicit reconciliation evidence rather than silent overwrites.

---

### C6 — Selected play-level reconciliation

Only after event/team/player crosswalks are stable enough.

For a bounded set of games, compare selected plays using combinations of:

```text
game
period
clock
down
distance
yardline
score
play text
play family
```

Do not assume provider play sequence numbers are canonical.

This pass should also quantify participant-link coverage where practical.

---

## 4. Game reconciliation contract

The C1 output must preserve per-source identity and acquisition context.

At minimum:

```text
season
cfbd_game_id
espn_game_id
id_match_state
cfbd_home_team
cfbd_away_team
espn_home_team
espn_away_team
team_name_match_state
week_match_state
kickoff_match_state
score_match_state
lifecycle_match_state
reconciliation_state
source_evidence
```

Expected game reconciliation states:

```text
DIRECT_PROVIDER_ID_MATCH
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
CFBD_ONLY
ESPN_ONLY
UNRESOLVED_UNIVERSE
```

A direct matching provider ID is strong crosswalk evidence but Daily-NCAAF still creates its own canonical `GAME_ID`.

---

## 5. Source immutability / reproducibility

Every downloaded public asset used in reconciliation must record:

```text
source_url
acquired_at
sha256
byte_count
```

CFBD requests must record their own acquisition time in the research output.

If the SportsDataverse release changes later, the old reconciliation result remains an observation of the bytes acquired at that time.

---

## 6. PIT boundary

B.2-C is an identity/source-reconciliation audit.

Successful historical matching does **not** make the matched source PIT-safe.

Continue to classify separately:

```text
historical truth
historical knowledge state
```

and:

```text
PIT-A / PIT-B / PIT-C / PIT-U
```

---

## 7. C1 harness

Initial tooling:

```text
scripts/probes/cross_provider_game_reconciliation_probe.py
tests/probes/test_cross_provider_game_reconciliation_probe.py
```

Default seasons:

```text
2024,2026
```

The probe is research-only and:

- reads `CFBD_API_KEY` from the environment;
- never emits the secret;
- downloads only public SportsDataverse schedule assets;
- records asset SHA-256;
- uses bounded CFBD 429 retry/backoff;
- never writes canonical identities;
- reports raw universe differences without declaring them missing data.

---

## 8. B.2-C exit criteria

B.2-C closes when representative evidence establishes defensible reconciliation behavior for:

1. games/events;
2. programs/teams;
3. players;
4. transfers;
5. venue/conference context;
6. selected play-level records where practical.

The output must identify both successful direct crosswalks and real ambiguity/failure states.

After B.2-C, remaining Phase B gates are B.2-D prospective revision/PIT capture and B.2-E availability-source trials before the production canonical schema is unlocked.