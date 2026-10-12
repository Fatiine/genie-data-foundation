# Data layout audit SQL

Replace placeholders safely and quote all identifiers. Run table-level commands
once per resolved table. A failed optional query means `not_observable`, not
`disabled`.

## Scope inventory

```sql
SELECT table_catalog, table_schema, table_name, table_type, table_owner,
       data_source_format, storage_path
FROM `<catalog>`.information_schema.tables
WHERE table_schema = <schema_literal>
  AND table_name IN (<table_literals>)
ORDER BY table_name;
```

## Physical layout

```sql
DESCRIBE DETAIL `<catalog>`.`<schema>`.`<table>`;
```

Capture at least `format`, `id`, `location`, `numFiles`, `sizeInBytes`,
`partitionColumns`, `clusteringColumns`, `properties`, and `tableFeatures`.
Compute average file size only when `numFiles > 0`.

```sql
SHOW TBLPROPERTIES `<catalog>`.`<schema>`.`<table>`;
```

Record `clusterByAuto` and explicit overrides related to:

- `delta.autoOptimize.*`
- `delta.targetFileSize`
- `delta.dataSkippingStatsColumns`
- `delta.dataSkippingNumIndexedCols`
- `delta.deletedFileRetentionDuration`
- `delta.logRetentionDuration`
- `delta.enableDeletionVectors`
- checkpoint and compatibility settings

## Predictive optimization state

Use JSON output when supported:

```sql
DESCRIBE TABLE EXTENDED `<catalog>`.`<schema>`.`<table>` AS JSON;
DESCRIBE SCHEMA EXTENDED `<catalog>`.`<schema>`;
DESCRIBE CATALOG EXTENDED `<catalog>`;
```

Capture the effective `Predictive Optimization` value and whether it is
inherited. When present, retain `predictive_optimization_evaluations` from the
table JSON.

## Delta maintenance history

```sql
SELECT
  version,
  timestamp,
  operation,
  CASE
    WHEN operationParameters.clusterBy IS NOT NULL
         AND operationParameters.clusterBy <> '[]' THEN 'LIQUID_CLUSTERING'
    WHEN operationParameters.zOrderBy IS NOT NULL
         AND operationParameters.zOrderBy <> '[]' THEN 'ZORDER'
    WHEN operationParameters.auto = 'true' THEN 'AUTO_COMPACTION'
    WHEN operation = 'OPTIMIZE' THEN 'MANUAL_OPTIMIZE'
    ELSE operation
  END AS operation_subtype,
  operationParameters,
  operationMetrics
FROM (
  DESCRIBE HISTORY `<catalog>`.`<schema>`.`<table>`
)
WHERE timestamp >= DATEADD(DAY, -<lookback_days>, CURRENT_TIMESTAMP())
ORDER BY version DESC;
```

For `OPTIMIZE`, inspect these `operationMetrics` keys when present:
`numAddedFiles`, `numRemovedFiles`, `numAddedBytes`, `numRemovedBytes`,
`minFileSize`, `p25FileSize`, `p50FileSize`, `p75FileSize`, and
`maxFileSize`.

## Predictive optimization operations

This system table requires account-level availability and permissions.

```sql
SELECT
  start_time,
  end_time,
  catalog_name,
  schema_name,
  table_name,
  operation_type,
  operation_status,
  operation_metrics
FROM system.storage.predictive_optimization_operations_history
WHERE catalog_name = <catalog_literal>
  AND schema_name = <schema_literal>
  AND table_name IN (<table_literals>)
  AND start_time >= DATEADD(DAY, -<lookback_days>, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

Relevant operation types include `COMPACTION`, `CLUSTERING`,
`AUTO_CLUSTERING_COLUMN_SELECTION`, `DATA_SKIPPING_COLUMN_SELECTION`,
`ANALYZE`, `VACUUM`, `DELETE`, and `PURGE`.

## Apply `CLUSTER BY AUTO`

Allowed only in `layout_mode = apply_approved` for an eligible approved table.
Execute this statement and nothing else:

```sql
ALTER TABLE `<catalog>`.`<schema>`.`<table>` CLUSTER BY AUTO;
```

Verify:

```sql
SHOW TBLPROPERTIES `<catalog>`.`<schema>`.`<table>` ('clusterByAuto');
DESCRIBE DETAIL `<catalog>`.`<schema>`.`<table>`;
```

Rollback when the table was previously unclustered:

```sql
ALTER TABLE `<catalog>`.`<schema>`.`<table>` CLUSTER BY NONE;
```

## Other proposed changes

Return these only as proposals. Never execute them from this skill.

```sql
ALTER TABLE `<catalog>`.`<schema>`.`<table>`
  ENABLE PREDICTIVE OPTIMIZATION;
```

Use `OPTIMIZE ... FULL` or a partition-to-liquid conversion only after checking
runtime support, workload evidence, cost, and operational impact. Do not emit
blanket SQL for every table.
