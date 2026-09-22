# Unity Catalog profiling SQL

Replace placeholders safely. Use the catalog's `information_schema`; use `system.information_schema` only when the caller has access and requests cross-catalog discovery.

## Tables and columns

```sql
SELECT t.table_catalog, t.table_schema, t.table_name, t.table_type,
       t.comment AS table_comment,
       c.ordinal_position, c.column_name, c.full_data_type,
       c.is_nullable, c.comment AS column_comment
FROM `<catalog>`.information_schema.tables t
JOIN `<catalog>`.information_schema.columns c
  USING (table_catalog, table_schema, table_name)
WHERE t.table_schema = <schema_literal>
  AND t.table_name IN (<table_literals>)
ORDER BY t.table_name, c.ordinal_position;
```

## Tags

```sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value
FROM `<catalog>`.information_schema.table_tags
WHERE schema_name = <schema_literal>
  AND table_name IN (<table_literals>);

SELECT catalog_name, schema_name, table_name, column_name, tag_name, tag_value
FROM `<catalog>`.information_schema.column_tags
WHERE schema_name = <schema_literal>
  AND table_name IN (<table_literals>);
```

## Constraints

```sql
SELECT tc.constraint_catalog, tc.constraint_schema, tc.constraint_name,
       tc.table_catalog, tc.table_schema, tc.table_name, tc.constraint_type,
       kcu.column_name, kcu.ordinal_position
FROM `<catalog>`.information_schema.table_constraints tc
LEFT JOIN `<catalog>`.information_schema.key_column_usage kcu
  USING (constraint_catalog, constraint_schema, constraint_name)
WHERE tc.table_schema = <schema_literal>
  AND tc.table_name IN (<table_literals>)
ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
```

Also inspect `referential_constraints` for FK targets.

## Exact key validation

```sql
SELECT
  COUNT(*) AS row_count,
  COUNT_IF(<null_predicate>) AS null_key_rows,
  COUNT(*) - COUNT(DISTINCT <key_struct>) AS duplicate_key_rows
FROM <qualified_table>;
```

For composite keys, use `COUNT(DISTINCT STRUCT(col1, col2, ...))`. Do not concatenate values.

## Foreign-key validation

```sql
SELECT COUNT(*) AS orphan_rows
FROM <child_table> c
LEFT ANTI JOIN <parent_table> p
  ON <null_safe_join_predicate>
WHERE <child_key_is_not_null>;
```

Do not use sampled data to claim zero duplicates or zero orphans. Approximate checks can reject candidates, but only full checks can validate them for publication.
