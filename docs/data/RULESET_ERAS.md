# Daily NCAAF — Ruleset & Competition Eras V1

**Phase:** B — Source & Coverage Audit  
**Status:** GOVERNING ERA REGISTRY V1; annual official-rule verification required  
**Audit date:** 2026-08-26

## Purpose

College football outcomes and statistics are generated under changing rules and competition structures. Daily NCAAF must not treat a 2005 game, a 2022 game, a 2024 game and a 2026 game as if the same clock, overtime, technology and postseason policies were in force.

This registry records rule changes that are material to state reconstruction, feature interpretation, simulation or model calibration. It is not intended to reproduce the entire NCAA rulebook.

Official NCAA/CFP sources are authoritative. Provider labels are secondary.

---

# Ruleset dimensions

Do not compress all historical variation into one opaque integer.

A game should eventually resolve at least:

```text
ruleset_version
clock_rule_version
overtime_rule_version
injury_timeout_rule_version
replay_rule_version
technology_rule_version
postseason_format_version
classification
conference_context_version
```

Some changes apply nationally; others apply by division or as conference experiments.

---

# Clock / timing eras

## CLOCK_PRE_2023_D1D2

For the modeling era before the 2023 Division I/II change, first downs in bounds used the older college-clock behavior: the game clock stopped for a first down and restarted after the chains were set/ready-for-play process.

Daily NCAAF historical reconstruction must preserve that older timing environment.

## CLOCK_2023_D1D2

Effective for NCAA Division I and Division II beginning in the 2023 season:

- when a runner gains a first down in bounds, the clock generally continues rather than stopping for the chains;
- the exception is during the final two minutes of each half, when the first-down clock-stop behavior remains;
- additional 2023 timing changes included restrictions on consecutive team timeouts and quarter-ending untimed-down administration.

Division III did not adopt the same first-down timing change until the following season.

**Model implications:**

- plays/drives per game;
- possession duration;
- late-half timing;
- scoring environment;
- simulation clock transitions;
- pace comparisons across eras.

## CLOCK_2024_ALL_DIVISIONS

Beginning in 2024, Division III adopted the first-down timing approach already used in Division I/II.

The 2024 rules also established an automatic two-minute timeout in the second and fourth quarters.

The simulation engine must therefore model a two-minute timeout event for applicable games and avoid treating old/new pace statistics as mechanically identical.

---

# Overtime eras

## OT_PRE_2019

Older NCAA overtime generally used alternating possessions beginning at the opponent 25-yard line, with required two-point attempts after later touchdowns under the rules then in force.

For Daily NCAAF, this era is a distinct simulation policy from the modern alternating two-point-shootout structure.

## OT_2019_2020

Beginning in 2019, the NCAA changed lengthy overtime procedures so that, if a game reached a fifth overtime, teams alternated two-point conversion plays rather than continuing full possessions from the 25-yard line.

This changed the scoring distribution of extreme-overtime games.

## OT_2021_2024

Beginning in 2021:

- after a touchdown in the second overtime, teams were required to attempt a two-point conversion;
- beginning with the third overtime, teams alternated two-point conversion attempts rather than full offensive possessions.

This is the major modern overtime state transition for simulation.

## OT_2025_PLUS

Beginning with the 2025 season, NCAA rules changed timeout treatment in extended overtime: each team receives one timeout beginning in the third overtime through the end of the game rather than refreshing a timeout in each overtime period.

The fundamental third-overtime alternating two-point structure remains the relevant scoring-state regime, with the updated timeout policy represented separately.

---

# Injury-timeout era

## INJURY_TIMEOUT_PRE_2025

Use the pre-2025 NCAA injury-timeout rules applicable to the game era.

## INJURY_TIMEOUT_2025_PLUS

Beginning in the 2025-26 rules cycle, if a player presents as injured after the ball has been spotted by the officials, the team can be charged a timeout; if no timeout remains, a delay-of-game penalty may apply under the new procedure.

This rule is relevant to:

- clock/timeout simulation;
- late-game strategy;
- injury event interpretation.

It is **not** evidence that injury-reporting quality improved in 2025; playing rules and pregame injury-information architecture remain separate concepts.

---

# Technology eras

## TECH_PRE_2024

No universal modern FBS coach-to-player helmet communication/tablet regime should be assumed for earlier seasons.

## TECH_2024_PLUS_FBS

Beginning in 2024, NCAA rules permitted FBS teams to use coach-to-player helmet communication for one player on the field, with communication cut off at the prescribed play-clock point or the snap. Tablets were also permitted for in-game viewing under the approved restrictions.

Potential future research questions include effects on:

- pace;
- defensive/offensive adjustment;
- sideline communication;
- inexperienced quarterback priors;
- home crowd/noise effects.

Do **not** hard-code a performance boost. Store the technology era first and test predictive value later.

## TECH_2026_REPLAY_EXPERIMENT

For 2026, NCAA-approved experimental replay technology can vary by conference/game rather than operating as a universal national rule. Conferences may experiment with real-time instant-replay video output to coaches' booths under approved conditions, and nonconference participation can depend on the visiting team's consent.

Represent this as a game/conference context flag:

```text
replay_experiment_enabled = true/false/unknown
```

not as a nationwide `2026 = new replay rules` assumption.

---

# CFP / postseason-format eras

## POSTSEASON_PRE_CFP

Seasons before the 2014-15 College Football Playoff are `PRE_CFP` for top-level postseason-format context.

This does not erase bowl-specific history; it only prevents the model from applying CFP seeding/hosting semantics to pre-CFP seasons.

## CFP_FOUR_TEAM_2014_2023

The four-team College Football Playoff era ran from the 2014-15 season through 2023-24.

Canonical postseason state must distinguish:

```text
CFP semifinal
CFP national championship
non-CFP bowl
conference championship
```

## CFP_TWELVE_TEAM_2024_PLUS

The expanded 12-team CFP began with the 2024-25 season. Official CFP materials confirm the 12-team structure continues for the 2026-27 season.

Daily NCAAF must represent:

- seed;
- first-round status;
- site/home-hosting context where applicable;
- quarterfinal/semi/championship stage;
- rest differential;
- neutral-site geography rather than a single postseason boolean.

If future CFP structure changes, create a new version instead of rewriting this era.

---

# Conference and classification eras are separate temporal context

Conference realignment is not an NCAA playing-rule version.

Represent independently:

```text
CONFERENCE_AFFILIATION_STINT
CLASSIFICATION_STINT
```

This matters because a program's opponent pool, championship path, travel pattern and schedule strength can change dramatically without any national playing-rule change.

Likewise, an FCS/FBS classification transition is program state, not a global ruleset version.

---

# COVID / irregular-season context

The 2020 season should carry an explicit structural-era/context flag because schedule length, conference participation, cancellations/postponements, attendance/crowd environment, player availability and data-generating processes were unusually nonstationary.

Conceptually:

```text
season_context = COVID_DISRUPTED
```

This is not one rule change. It is a modeling/evaluation regime requiring subgroup analysis and potentially different missingness policies.

Do not discard 2020 automatically; model/evaluate it explicitly.

---

# Stat interpretation across eras

Rule changes can alter the meaning/distribution of metrics even when column names remain the same.

Examples:

```text
plays_per_game
seconds_per_play
possessions_per_game
late-half drive count
overtime points
final margin
total points
```

Daily NCAAF therefore should not solve era change by merely normalizing raw values globally.

Models may use:

- ruleset categorical/context features;
- era-conditioned baselines;
- hierarchical partial pooling;
- era-aware simulation policies;
- walk-forward calibration checks.

---

# Play-by-play normalization rule

Canonical play semantics should describe what happened under the applicable historical rules.

Do not rewrite old plays as if current rules applied.

Example:

```text
2018 first down
```

must retain its actual clock-state consequence under the 2018 rule environment.

The simulation engine later uses the game's `clock_rule_version` to decide how an equivalent modeled play changes the game clock.

---

# Overtime labeling rule

Store enough state to identify:

```text
regulation vs overtime
overtime_number
possession/attempt type
full possession vs two-point shootout
score before/after
```

A third-overtime two-point attempt under the modern rules is not semantically equivalent to a conventional drive from the 25-yard line in an older era.

---

# Rules source hierarchy

For ruleset disputes:

1. NCAA official playing-rules publications/announcements;
2. CFP official materials for CFP format;
3. official conference documentation for approved experiments/local competition context;
4. provider metadata;
5. secondary reporting.

Secondary articles can aid discovery but should not become the governing rule record when an official source is available.

---

# Annual ruleset review

Before every season, Daily NCAAF must perform a rules audit covering at least:

```text
clock rules
overtime
kickoff / kicking rules
replay
technology
player eligibility substitutions relevant to game state
injury timeout rules
postseason format
conference experiments
classification/conference changes
```

Output:

```text
RULESET_REVIEW_<season>.md
```

Any material change produces a new version rather than silently editing historical semantics.

---

# Initial era registry

| Dimension | Version | Effective scope |
|---|---|---|
| clock | `CLOCK_PRE_2023_D1D2` | older D1/D2 modeling era |
| clock | `CLOCK_2023_D1D2` | 2023 D1/D2 |
| clock | `CLOCK_2024_ALL_DIVISIONS` | 2024+ common first-down/two-minute-timeout era |
| overtime | `OT_PRE_2019` | pre-2019 |
| overtime | `OT_2019_2020` | 2019-2020 |
| overtime | `OT_2021_2024` | 2021-2024 |
| overtime | `OT_2025_PLUS` | 2025+ timeout-adjusted modern OT |
| injury timeout | `INJURY_TIMEOUT_PRE_2025` | pre-2025 |
| injury timeout | `INJURY_TIMEOUT_2025_PLUS` | 2025+ |
| technology | `TECH_PRE_2024` | pre-2024 baseline |
| technology | `TECH_2024_PLUS_FBS` | 2024+ FBS helmet/tablet environment |
| replay experiment | `TECH_2026_REPLAY_EXPERIMENT` | participating 2026 games only |
| postseason | `POSTSEASON_PRE_CFP` | through 2013 season |
| postseason | `CFP_FOUR_TEAM_2014_2023` | 2014-2023 seasons |
| postseason | `CFP_TWELVE_TEAM_2024_PLUS` | 2024+ until superseded |
| structural season | `COVID_DISRUPTED` | 2020 context |

---

# Scope caution

This V1 registry identifies the currently verified high-impact changes relevant to the planned modern historical modeling horizon. It is **not yet a complete year-by-year codification of every NCAA rule amendment since 2004**.

Before Phase C locks game-state simulation fields, the empirical/official-source follow-up should verify whether additional changes materially affect:

- kickoff touchback/onside behavior;
- targeting/ejection state;
- replay review procedures;
- extra-point/field-goal administration;
- clock runoff/penalty timing;
- substitution mechanics;
- statistical scoring definitions.

If material, those become additional independently versioned dimensions.

---

# Reviewed official sources

- NCAA football playing-rules hub: https://www.ncaa.org/championships/playing-rules/football-playing-rules/
- NCAA 2023 football timing-rule change materials
- NCAA 2024 football rules/technology change materials
- NCAA 2025 football rules change materials
- NCAA 2019 overtime rule change materials
- NCAA 2021 overtime rule change materials
- College Football Playoff official history: https://collegefootballplayoff.com/sports/2026/8/10/cfp-history.aspx
- College Football Playoff 2026-27 format announcement: https://collegefootballplayoff.com/news/2026/1/23/2627-format.aspx

---

# Locked consequence for Phase C/F-17

The canonical `GAME`/simulation state must be able to resolve rule dimensions by game date, division/classification and competition context.

A single boolean such as:

```text
modern_rules = true
```

is explicitly insufficient.
