---
name: catalog-semantic-profiler
description: Profiles a supplied Unity Catalog table list or catalog pattern for schemas, comments, tags, constraints, lineage clues, keys, grain, and relationship evidence. Use before enriching catalog metadata or building semantic and metric views.
---

# Catalog semantic profiler

Inspect only the requested Unity Catalog scope. This skill is read-only.

## Required inputs

- `table_scope`: explicit fully qualified table names, or a catalog/schema pattern.
- Optional `profile_level`: `metadata` (default) or `bounded_data`.
- Optional limits: maximum tables, rows sampled, runtime, and cost.

Expand patterns and show the resolved table list before profiling. Exclude views unless the user includes them.

## Workflow

1. Resolve and validate the scope.
2. Query information schema for tables, columns, comments, tags, and constraints using [sql-templates.md](sql-templates.md).
3. Run `DESCRIBE DETAIL` or `SHOW CREATE TABLE` only where information schema is insufficient.
4. In `bounded_data` mode, profile candidate key and relationship columns:
   - row count or bounded approximation
   - null count
   - distinct count
   - duplicate key groups
   - minimum/maximum for dates and numerics
   - candidate FK orphan count
5. Infer table grain only when supported by declared keys or validated uniqueness.
6. Return a catalog snapshot and validation evidence. Do not alter any object.

## Candidate discovery

Prioritize columns explicitly named by supplied document evidence. Otherwise, candidate signals may include:

- names ending in `_id`, `_key`, `_code`, or stable business identifiers
- exact datatype-compatible names across in-scope tables
- existing PK/FK constraints
- table and column comments

Name similarity creates a candidate only; it never proves a key or relationship.

## Data safety

- Quote all identifiers and escape literals.
- Avoid `SELECT *` from data tables.
- Use aggregate checks and bounded samples.
- State when profiling is approximate.
- Stop if the requested scope unexpectedly expands beyond the supplied maximum.
- Never expose sampled sensitive values in the report.

## Output

Return:

- resolved table inventory with formats and ownership
- columns, datatypes, nullability, comments, and tags
- current PK/FK/unique constraints
- candidate keys and joins with validation results
- likely grain and time dimensions
- conflicts with supplied document evidence
- permissions or runtime limitations

Use fully qualified names in every output record.
