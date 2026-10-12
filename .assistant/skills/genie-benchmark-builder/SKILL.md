---
name: genie-benchmark-builder
description: Scopes a Genie Agent domain from a supplied question list, maps questions to Unity Catalog evidence, builds and validates benchmark ground-truth SQL, publishes explicitly approved benchmarks, and optionally runs a baseline evaluation. Use when designing, reviewing, or maintaining Genie Agent benchmarks.
---

# Genie benchmark builder

Turn realistic user questions into a bounded domain scope and a reviewed Genie
benchmark set. Default to `dry_run`. Publishing always requires
`apply_approved`.

Benchmarks are evaluation assets only. Never present them as instructions,
example SQL, training data, or context that improves Genie answers.

## Required inputs

- `questions`: inline questions or a `.txt`, `.csv`, or `.json` path,
  preferably in a Unity Catalog Volume.
- `table_scope`: explicit fully qualified objects or one bounded schema pattern.
  When omitted, use only the existing Genie Agent data sources.
- `warehouse_id`: SQL warehouse used to validate candidate ground truth.
- Optional `space_id`: existing Genie Agent. Required for publication.
- Optional `mode`: `dry_run` (default) or `apply_approved`.
- Optional `approved_question_ids`: required for `apply_approved`.
- Optional `output_path`: artifact directory. Defaults to
  `/Workspace/.assistant/runs/<run_id>/benchmark/`.
- Optional `run_evaluation_after_publish`: default `false`.
- Optional limits: maximum 500 benchmark questions, maximum tables, runtime,
  result rows, and query cost.

Reject unbounded metastore discovery. Fetching an existing agent requires at
least view permission; publishing requires edit permission.

## Workflow

1. Normalize and deduplicate questions.
2. Fetch the current Genie Agent when `space_id` is supplied. Parse but preserve
   its complete `serialized_space`.
3. Resolve a bounded candidate data scope and profile catalog metadata,
   relationships, grains, metrics, and documented business rules.
4. Classify each question using [benchmark-contract.md](benchmark-contract.md).
5. Recommend the smallest coherent domain that covers the answerable questions.
6. Generate and validate candidate ground-truth SQL only for `in_scope`
   questions.
7. Write review artifacts using [benchmark-review.sql](benchmark-review.sql)
   and [benchmark-review-notebook.py](benchmark-review-notebook.py).
8. In `apply_approved`, publish only approved, validated questions using
   [api-templates.md](api-templates.md).
9. Optionally run a baseline chat-mode evaluation for the newly published IDs.

## Question identity and grouping

- Normalize whitespace for comparison but preserve the submitted text.
- Derive a stable 32-character hexadecimal ID from the normalized question
  text and domain identifier. Preserve an existing benchmark ID when the
  question already exists.
- Group equivalent phrasings under one `intent_id`; each phrasing remains a
  separate benchmark question with the same approved SQL.
- Detect exact and semantic duplicates before publication.
- Recommend at least five total questions and two to four realistic phrasings
  for important intents, without exceeding the platform limit of 500.

## Domain scoping

Classify every question as:

- `in_scope`: one validated interpretation is answerable from the allowed data.
- `partially_answerable`: only part of the request is supported.
- `ambiguous`: multiple material interpretations remain.
- `out_of_scope`: required data or business semantics are absent.

For every classification, retain:

- required tables or metric views
- columns, joins, measures, filters, time semantics, and answer grain
- catalog or document evidence
- missing data or semantics
- confidence and rationale

Do not convert `partially_answerable`, `ambiguous`, or `out_of_scope` questions
into SQL benchmarks. Return the clarification or data gap instead.

Recommend a focused domain. Prefer five or fewer data sources when they can
cover the approved questions, but do not remove a required source merely to
meet that guideline. Domain recommendations do not modify the agent's data
sources.

## Ground-truth SQL

Generate SQL only after the question is `in_scope`.

- Allow one read-only `SELECT` or `WITH` statement.
- Use fully qualified objects within `table_scope` or existing agent sources.
- Use validated joins, metrics, filters, time definitions, and grain.
- Select explicit columns; never use `SELECT *`.
- Make aliases stable and meaningful.
- Do not use `LIMIT`, ordering, rounding, or null substitution unless the
  question or business rule requires it.
- Use concrete benchmark values rather than unresolved parameters.
- Avoid non-determinism. If relative time is intentional, record its exact
  semantics and expected result volatility.
- Do not expose sensitive row-level data in artifacts or logs.

Validate each candidate:

1. Parse or explain the SQL.
2. Verify every object and column is in scope.
3. Verify join cardinality and expected answer grain.
4. Execute with a bounded timeout on `warehouse_id`.
5. Record result schema, row count, and a non-reversible result signature; do
   not persist result rows.
6. Mark empty, excessively large, unstable, or permission-limited results as
   `review_required`.

Generated and executed SQL is still only a candidate. A reviewer must set
`review_status: approved` before it becomes ground truth.

## Review artifacts

Write:

- `domain_scope.json`: per-question classification and coverage matrix
- `benchmark_questions.json`: Genie-compatible benchmark objects
- `benchmark_review.sql`: candidate SQL with evidence and validation comments
- `benchmark_review.py`: Databricks notebook for reviewer decisions
- `run_report.json`: counts, gaps, conflicts, and permissions

Do not include raw query results. Use [benchmark-contract.md](benchmark-contract.md)
for the required fields.

## Apply approved benchmarks

Publication is allowed only when:

- `mode` is `apply_approved`
- `space_id` and `approved_question_ids` are explicit
- every approved question is `in_scope`
- SQL validation succeeded and `review_status` is `approved`
- the live agent still matches the captured `etag` or configuration hash

Before update:

- re-fetch the live agent
- persist `genie_space.before.json`
- merge approved questions into `benchmarks.questions`
- preserve every unrelated serialized field and benchmark
- treat an exact existing benchmark as `already_applied`
- block conflicting IDs, changed answers, deletion, or replacement

After update:

- re-fetch and persist `genie_space.after.json`
- verify each approved ID and answer
- write request, response, before/after hashes, and rollback payload to the
  applied-actions ledger

Never report success without post-update verification and artifact paths.

## Baseline evaluation

When `run_evaluation_after_publish` is true, start a chat-mode benchmark run
for only the newly published IDs. Record the run ID, result IDs, completion
status, accuracy, needs-review count, and assessment reasons.

The public evaluation API is capability-dependent. Do not claim Agent-mode
evaluation unless the live API explicitly supports it. A failed evaluation
does not roll back correctly published benchmarks; report it separately.

## Output

Return:

- domain coverage and recommended data sources
- benchmark candidates grouped by intent
- approved, rejected, ambiguous, partial, and out-of-scope counts
- SQL validation summary and review-required items
- artifact paths
- publication status, backup, verification, and rollback paths
- optional evaluation run summary
