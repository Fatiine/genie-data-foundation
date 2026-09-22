---
name: semantic-view-builder
description: Designs and creates governed Databricks relational views and Unity Catalog metric views from validated catalog relationships and documented business definitions. Use to expose bronze or base tables safely to Genie and analytics users.
---

# Semantic view builder

Build a semantic layer from validated metadata. Never invent business formulas.

## Required inputs

- Explicit source `table_scope`.
- Validated keys, relationships, grains, and document evidence.
- `target_schema` distinct from the source bronze schema.
- `mode`: `dry_run`, `apply_approved`, or `auto_apply_high_confidence`.
- Optional naming prefix and supported Databricks Runtime/SQL Warehouse version.

## Choose the asset

- Use a standard view to rename fields, cast types, filter technical rows, or present a validated join.
- Use a metric view for reusable dimensions and aggregate measures.
- Keep separate fact grains in separate metric views unless a documented bridge prevents fanout.

## Standard views

1. Select columns explicitly; never expose `*`.
2. Preserve source keys needed for joins.
3. Rename only from documented business terms.
4. Add table and column comments.
5. Do not hide restatement, currency, unit, or frequency semantics.
6. Use schema binding/evolution behavior deliberately for the supported runtime.

## Metric views

Use YAML specification `1.1` only when supported; otherwise generate a review artifact compatible with the available runtime. Follow [metric-view-template.md](metric-view-template.md).

- Source must be fully qualified.
- Fields need expressions and evidence-backed comments.
- Measures need explicit aggregation, grain, unit/currency behavior, and null handling.
- Joins require validated columns and cardinality.
- Set `at_most_one_match: true` only after uniqueness validation.
- Prefer additive measures. Mark semi-additive and non-additive metrics for review unless the document defines the behavior.
- A numeric column is not automatically a `SUM`.
- Ratios must use documented numerator and denominator; use safe division.
- Do not mix preliminary, final, and restated values without an explicit rule.

## Automatic creation

In `auto_apply_high_confidence`, create an asset only when:

- every source object is in scope and readable
- the target schema is explicitly supplied
- all joins and formulas meet publication thresholds
- generated SQL/YAML parses and a limited preview succeeds
- no target object exists, or the existing object carries the workflow ownership tag and its stored source hash matches the managed lineage

Never replace an unowned object. If a name collides, produce a new proposal.

## Validation

Before apply:

- compile or explain the standard view query
- parse metric YAML
- validate all referenced columns
- test join fanout and expected grain
- preview dimensions and measures without exposing sensitive values
- compare row counts before and after joins

After apply:

- query the object
- verify comments/tags
- run one dimension-only and one measure query
- record the definition hash and rollback (`DROP VIEW`) statement

## Output

Return the proposed or applied SQL/YAML, source evidence, grain, joins, dimensions, measures, validation results, ownership status, and review items.
