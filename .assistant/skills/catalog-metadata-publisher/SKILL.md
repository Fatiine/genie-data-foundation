---
name: catalog-metadata-publisher
description: Matches document evidence to Unity Catalog objects and safely publishes table and column comments, tags, and informational PK/FK constraints. Use after document extraction and catalog profiling, or to generate reviewable metadata DDL.
---

# Catalog metadata publisher

Publish only evidence-backed, validated metadata. Default to `dry_run` unless the caller explicitly requests apply or an orchestrator supplies `auto_apply_high_confidence`.

## Required inputs

- Extracted evidence conforming to [proposal-contract.md](proposal-contract.md), or equivalent document evidence.
- Catalog profile for an explicit `table_scope`.
- `mode`: `dry_run`, `apply_approved`, or `auto_apply_high_confidence`.

## Match and propose

1. Match exact qualified names first.
2. Then match exact case-insensitive and normalized names within the supplied scope.
3. Treat fuzzy, many-to-one, and cross-schema matches as review-only.
4. Require datatype compatibility for column matches and key relationships.
5. Produce proposals before executing any DDL.

## Automatic publication thresholds

In `auto_apply_high_confidence`, an action is eligible only when all rules for its type pass:

- **Table/column comment:** confidence `>= 0.95`, one unambiguous match, explicit source evidence, and no conflicting curated comment.
- **Tags:** confidence `>= 0.95`, tag is allow-listed, value is valid, and no conflicting governed tag exists.
- **Primary key:** explicit declared evidence at `1.00`; columns exist and are catalog-non-nullable; a full-data check has zero null and duplicate rows.
- **Foreign key:** explicit declared evidence at `1.00`; parent PK/unique constraint exists or is approved in the same run; types and column order match; full-data orphan count is zero.

Never automatically:

- overwrite a non-empty differing comment
- unset tags
- change column nullability
- add a `RELY` option unless full cardinality/integrity checks pass and policy permits it
- publish an inferred PK/FK
- operate outside `table_scope`

## Apply safely

Use templates in [sql-templates.md](sql-templates.md).

1. Capture current metadata and generate inverse/rollback statements.
2. Order operations: comments/tags, parent keys, then foreign keys.
3. Use stable names no longer than the platform limit.
4. Execute one proposal at a time and record its result.
5. Re-query information schema to verify the outcome.
6. A failed action must not cause later dependent actions to run.

PK, FK, and unique constraints in Databricks are informational and require Delta/Unity Catalog support. State this in the report.

## Output

Return applied, skipped, conflicted, failed, and review-required actions. Each record must contain:

- target object
- action and generated SQL
- confidence and rationale
- source document/page/excerpt
- validations performed and results
- before/after state
- rollback SQL when applicable

Never report success without post-application verification.
