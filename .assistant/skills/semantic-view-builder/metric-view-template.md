# Metric view template

Use only supported fields for the active metric-view YAML version. Prefer stable snake_case names and user-facing display names where supported.

```sql
CREATE VIEW `<target_catalog>`.`<target_schema>`.`<metric_view>`
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "<evidence-backed purpose>"
source: <source_catalog>.<source_schema>.<source_table>
joins:
  - name: <dimension_alias>
    source: <catalog>.<schema>.<dimension_table>
    'on': source.<foreign_key> = <dimension_alias>.<primary_key>
    rely:
      at_most_one_match: true
fields:
  - name: <field_name>
    expr: source.<column>
    comment: "<documented meaning>"
    synonyms:
      - "<documented synonym>"
measures:
  - name: <measure_name>
    expr: SUM(source.<measure_column>)
    comment: "<definition, grain, unit, and exclusions>"
$$;
```

Omit `joins`, `synonyms`, or other optional properties when unavailable or unsupported. Do not leave placeholders in generated SQL.

## Safe ratio pattern

Use the platform-supported safe division function or:

```sql
SUM(source.<numerator>) / NULLIF(SUM(source.<denominator>), 0)
```

Only use this pattern when the document defines the ratio as a ratio of sums. It is not equivalent to averaging row-level ratios.

## Join validation

For each join, capture:

- child and parent columns and datatypes
- parent duplicate/null counts
- child orphan count
- base row count
- joined row count
- expected cardinality

Omit `rely.at_most_one_match` unless the parent key is fully validated.

## Ownership metadata

After creation, tag the view using an approved tag namespace, for example:

- `semantic_generator = genie_semantic_skills`
- `semantic_definition_hash = <hash>`
- `semantic_run_id = <run_id>`

If these tags are unavailable, maintain equivalent ownership in the run report. Ownership metadata must not overwrite governed tags.
