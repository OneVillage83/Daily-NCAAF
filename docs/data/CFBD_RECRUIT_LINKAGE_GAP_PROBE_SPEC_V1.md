# Daily NCAAF — CFBD Recruit Linkage Gap Probe Spec V1

**Phase:** B.2-B — Targeted Identity Cases  
**Status:** ACTIVE  
**Purpose:** measure how CFBD identity behaves when recruiting `athleteId` is absent, and surface unsafe name-collision cases.

---

## 1. Research question

The positive identity cases proved that recruiting `athleteId` can directly link recruiting records to stable roster athlete IDs when present.

However broad recruiting measurement showed that `athleteId` is absent for a material share of recruits.

This probe asks:

```text
When recruit.athleteId is null,
can the later roster row's recruitIds recover a direct provider link?
```

and, if not:

```text
what contextual evidence remains and where is name matching ambiguous?
```

---

## 2. Governing safety rule

```text
NAME MATCH != IDENTITY MATCH
```

Exact normalized names may locate candidate rows for audit purposes only.

The probe must never assign a canonical player identity.

Allowed interpretations:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
AMBIGUOUS_NAME_COLLISION
UNRESOLVED
```

Only the first state is an explicit provider-link recovery.

---

## 3. Target years

Initial bounded scan:

```text
2021
2022
2023
2024
```

These seasons are modern enough to have useful roster/recruiting coverage while spanning the observed direct-link incompleteness.

---

## 4. Candidate selection

For each year:

1. fetch the season-specific FBS program set;
2. fetch high-school recruiting rows;
3. filter to rows where:
   - `athleteId` is null;
   - `committedTo` is a measured FBS program;
   - recruiting record ID and name are present;
4. select a small deterministic sample, prioritizing higher-ranked records where ranking exists;
5. query the committed program's roster for the same season;
6. if no exact-name candidate is observed, query the following season as a bounded fallback.

This is a research sample, not an estimate of national reconciliation success rate.

---

## 5. Direct provider-link recovery

For each roster candidate, inspect:

```text
roster.recruitIds
```

If the recruiting record's provider recruit ID appears in that list, classify:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK
```

This is direct provider evidence despite the recruiting row lacking `athleteId`.

If an exact-name candidate exposes one stable roster athlete ID but does not carry the recruit ID, classify only:

```text
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
```

Do not promote it automatically.

If multiple candidate roster IDs share the normalized name, classify:

```text
AMBIGUOUS_NAME_COLLISION
```

If no candidate is found:

```text
UNRESOLVED
```

---

## 6. Name-collision audit

Within each recruiting-year response, group rows by normalized name.

Surface bounded examples where one normalized name maps to multiple recruiting records, including:

```text
recruit record ID
name
committedTo
position
athleteId
```

This provides empirical evidence for the rule that names cannot be primary keys even before roster reconciliation.

Duplicate-name records are not automatically duplicate people; they are ambiguity evidence.

---

## 7. Output contract

Top-level output must include:

```text
contract_version
research_only
generated_at
secret_policy
years
max_cases_per_year
request_delay_seconds
max_429_retries
status
results
```

Each year should include:

```text
FBS/recruiting HTTP state
recruit row count
athleteId-null count
FBS-committed athleteId-null count
selected missing-link cases
normalized-name collision examples
```

Each selected case records only bounded fields needed for the audit.

---

## 8. Reliability / secret policy

- `CFBD_API_KEY` comes from the local environment only.
- Never emit the key.
- Use paced requests.
- Retry HTTP 429 with bounded backoff / `Retry-After` support.
- HTTP failure remains a transport state, not a data-coverage result.
- Research tooling must remain separate from production acquisition.

---

## 9. Exit criterion

This probe completes the remaining B.2-B recruit-linkage hard case when it demonstrates at least one of the following with explicit evidence:

1. missing recruiting `athleteId` can sometimes be recovered through roster `recruitIds`;
2. missing `athleteId` can leave only contextual/name evidence;
3. normalized-name collisions make automatic merging unsafe.

After documenting those outcomes, B.2-B can close unless a new provider-identity failure mode appears.

Then advance to:

```text
B.2-C — CFBD <-> ESPN/cfbfastR reconciliation
```
