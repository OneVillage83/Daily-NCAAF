# Daily NCAAF Football State Architecture

**The Daily Line — Daily NCAAF**  
**F-5 through F-9 — Version 1.0**  
**Status: LOCKED V1**

## Purpose

This document defines how normalized evidence becomes canonical football state. Daily NCAAF models interacting program, player, unit, coaching, and play states rather than treating a team as one timeless rating.

---

# F-5 — Canonical Game / Drive / Play Architecture

## F-5.1 Event hierarchy

```text
GAME
  ↓
POSSESSION
  ↓
DRIVE
  ↓
PLAY
  ↓
PLAY EVENT
  ↓
PARTICIPATION
```

Provider schemas may differ. The canonical hierarchy models football reality and preserves source lineage.

## F-5.2 Play execution family

Use `PLAY_EXECUTION` as the parent concept. Do not use `PLAY_ACTION`, because play action is a real football design modifier.

Initial execution families:

```text
PASS
RUSH
SCRAMBLE
SACK
KNEEL
SPIKE
PUNT
FIELD_GOAL
KICKOFF
EXTRA_POINT
TWO_POINT
PENALTY_ONLY
TIMEOUT
ADMIN
OTHER
```

## F-5.3 Design modifiers are separate

A play may carry modifiers such as play action, RPO, option family, designed QB run, screen, draw, motion, shift, formation, personnel, dropback type, run direction, pressure context, and coverage family where supported.

## F-5.4 Canonical play state

Preserve where available:

- game/drive/possession identity
- offense/defense
- period and clock
- down/distance
- yards to goal
- score state
- execution family
- design modifiers
- result
- penalties
- turnovers
- scoring state
- source/reconciliation metadata

## F-5.5 Pre-snap and post-snap separation

State knowable before the snap must remain separable from the outcome produced by the snap so later next-play and simulation models cannot leak target information.

## F-5.6 Penalties, turnovers, and special teams

Represent penalties and turnovers structurally rather than reducing everything to net yardage. Punts, kicks, and returns are first-class football events because they change scoring and field-position distributions.

## F-5.7 Ruleset and overtime

Associate event state with `ruleset_version`. College overtime, clock, replay, and related rules vary by era.

## F-5.8 Participation confidence

Observed participation and reconstructed participation are distinct. Estimated personnel must carry provenance/confidence rather than being stored as exact truth.

## F-5.9 Blowout context

Do not delete late-game evidence. Preserve score/time/participation state so later feature versions can identify low-leverage or reserve-heavy snaps and test alternative weighting rules.

**F-5 status: LOCKED V1.**

---

# F-6 — Program / Team State Engine

## F-6.1 Team state is dynamic

Conceptually:

```text
PROGRAM_STATE

program_season_id
as_of

offense_state
defense_state
special_teams_state
roster_state
continuity_state
depth_state
schedule_context
uncertainty
```

## F-6.2 State families

Candidate dimensions include opponent-adjusted efficiency, success rate, big-play creation/prevention, pass/rush performance, early-down and passing-down behavior, finishing drives, pressure/sack state, turnover process, pace, and field position.

## F-6.3 Opponent adjustment is mandatory

College schedule strength varies dramatically. Raw production cannot be interpreted without opposition context. The architecture must support hierarchical adjustment across national, classification/level, conference/schedule ecosystem, program, and opponent interaction.

## F-6.4 State evolves through time

Recent evidence and older evidence may receive different weights using validated dynamic methods such as state-space updating, filtering, or recency weighting. The exact method is a modeling choice; time-varying state is an architectural requirement.

## F-6.5 Offseason transition inputs

Program priors may incorporate returning snaps/starts, QB continuity, OL continuity, skill/defensive continuity, recruiting/talent, transfers, departures, and coaching changes. These are probabilistic inputs, not deterministic quality scores.

## F-6.6 State uncertainty

Expose uncertainty created by small samples, new staffs, large roster turnover, unresolved QB competition, weak data, and cross-level opponents.

**F-6 status: LOCKED V1.**

---

# F-7 — Player State Engine

## F-7.1 Talent vs program-conditioned state

```text
PLAYER_TALENT_STATE
        +
ROLE / SCHEME / TEAM CONTEXT
        ↓
PLAYER_PROGRAM_CONDITIONED_STATE
```

A transfer preserves identity and some underlying skill evidence while role, teammates, coaching, scheme, and competition level change.

## F-7.2 Player-state dimensions

Potential dimensions include talent prior, current performance, role, expected starter probability, snap share, usage, workload, availability, experience, eligibility, position, opponent-adjusted production, and uncertainty.

## F-7.3 Low-sample priors

For players with little college evidence, priors may use recruiting evaluation, position, athletic testing, prior-school production, age/eligibility, and depth competition where defensibly sourced. Uncertainty must be high until college evidence accumulates.

## F-7.4 Transfer rule

On transfer:

- preserve canonical player identity;
- retain prior-school evidence;
- carry talent state with uncertainty;
- re-estimate role and program-conditioned state;
- update competition/scheme/team context;
- never assume equal production portability.

## F-7.5 Position is time-varying

Position changes update state/stints without creating a new player.

## F-7.6 Quarterback state

QB state warrants explicit treatment of passing, pressure response, sack avoidance, rushing value, designed-run usage, turnover process, experience in system, and expected starter probability.

## F-7.7 Availability link

Availability is supplied by F-10 as a distribution/scenario input; it is not permanently compressed into one healthy/injured flag.

**F-7 status: LOCKED V1.**

---

# F-8 — Unit State Engine

## F-8.1 Core units

Offense: quarterback room, offensive line, running backs, receiving unit, tight ends where useful.

Defense: defensive front, edge/pass rush, linebackers, secondary, coverage unit.

Special teams: kicking, punting, return, and coverage.

## F-8.2 Configuration-aware state

Unit strength depends on expected participants and roles. When availability is unresolved, support multiple plausible configurations rather than one assumed lineup.

## F-8.3 Depth is explicit

Distinguish starter quality, rotation quality, replacement quality, and depth uncertainty. A starter loss has different impact depending on the replacement distribution.

## F-8.4 Matchup interactions

Support interactions such as:

```text
pass protection ↔ pass rush
run blocking ↔ defensive front
QB pressure response ↔ pressure creation
receiving quality ↔ coverage quality
big-play creation ↔ big-play prevention
QB/run scheme ↔ defensive structure
pace ↔ opponent depth/substitution
special teams ↔ field-position response
```

## F-8.5 Rotation and low-leverage participation

College teams rotate personnel heavily and use reserves in lopsided games. Unit learning must be able to distinguish starter evidence from reserve-heavy snaps.

## F-8.6 Cohesion/continuity

Potential unit continuity signals include returning OL starts/snaps, QB-receiver continuity, secondary continuity, and coordinator/system continuity. Predictive value must be validated out of time.

**F-8 status: LOCKED V1.**

---

# F-9 — Coaching & Scheme State Engine

## F-9.1 Persistent staff identity

Maintain canonical coach identities and program-role stints for head coach, offensive coordinator, defensive coordinator, special-teams coordinator, play caller, and later position coaches where useful.

## F-9.2 Coaching regimes are time-versioned

Midseason or interim changes create new effective regimes rather than overwriting season history.

## F-9.3 Scheme is empirical state

Narrative labels can be retained as metadata, but modeling should derive measurable tendencies where possible.

Offensive candidates include tempo, neutral pass rate, early-down pass rate, RPO rate, option rate, designed-QB-run rate, play-action rate, motion, personnel usage, fourth-down aggression, and red-zone behavior.

Defensive candidates include front structure, pressure tendency, coverage-family distribution, box structure, and big-play prevention profile.

## F-9.4 Play-caller identity is distinct

Coordinator title and actual play caller may differ; preserve both where defensibly known.

## F-9.5 Coaching transitions

New-staff priors can use coach history, coordinator history, prior tendencies, retained roster, transfers, and program context. Prior tendencies must not be assumed to transfer perfectly to a new roster.

## F-9.6 Coaching decision policy

Future simulation may model fourth-down decisions, tempo changes, two-point decisions, timeout use, and end-of-half behavior conditional on state.

## F-9.7 Scheme diversity

College scheme diversity is materially wider than the NFL. The architecture must accommodate option-heavy, tempo-heavy, spread, Air-Raid-like, QB-run-heavy, power, and other systems without forcing them into one scheme prior.

**F-9 status: LOCKED V1.**

---

# F-5 through F-9 Definition of Done

Implementation must eventually support provider-independent play state, pre/post-snap separation, blowout/participation context, dynamic opponent-adjusted program state, transfer-safe player state, depth-aware unit configurations, time-versioned coaching regimes, empirical scheme state, and uncertainty propagation.

**F-5 through F-9: LOCKED V1.**
