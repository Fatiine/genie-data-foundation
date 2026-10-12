---
name: data-layout-auditor
description: Audits Unity Catalog tables for liquid clustering, predictive optimization, partitioning, file layout, Delta maintenance, and related performance practices; optionally applies CLUSTER BY AUTO to explicitly approved eligible tables. Use when assessing table layout health, preparing optimization recommendations, or enabling automatic liquid clustering after review.
---

# Data layout auditor

Audit the requested Unity Catalog scope first. Default `layout_mode` is
`dry_run`: return evidence and proposed SQL, and execute no layout DDL.

The only mutating action this skill may ever run is `CLUSTER BY AUTO`, and
only under `apply_approved`. Never run `OPTIMIZE`, `VACUUM`, `ANALYZE`,
`REORG`, partition conversion, manual `CLUSTER BY` keys, or predictive
optimization enablement.

## Required inputs

- `table_scope`: explicit fully qualified tables or one bounded schema pattern.
- Optional `lookback_days`: default 30.
- Optional `audit_level`: `metadata` (default), `history`, or `workload`.
- Optional `layout_mode`: `dry_run` (default) or `apply_approved`.
- Optional `allowed_layout_actions`: default empty. The only supported value
  is `cluster_by_auto`.
- Optional `approved_tables`: fully qualified tables that may receive an
  allowed action. Required for `apply_approved`.
- Optional `ledger_path`: Volume or Workspace folder for the applied-actions
  ledger. Defaults to `/Workspace/.assistant/runs/<run_id>/`.
- Optional limits: maximum tables, runtime, and query-history cost.

Resolve patterns and show the table list before auditing. Exclude views unless
the caller explicitly requests them. `auto_apply_high_confidence` is not a
valid layout mode.

## Workflow

1. Establish runtime capabilities and permissions.
2. Inventory table type, provider, ownership, size, file count, partitions,
   properties, features, and clustering state using
   [sql-templates.md](sql-templates.md).
3. Resolve the effective predictive optimization state at table, schema, and
   catalog level. Preserve whether the value is explicit or inherited.
4. For `history`, inspect Delta history and predictive optimization operations.
5. For `workload`, inspect authorized query history for recurring filters,
   joins, aggregations, and scan selectivity. Do not expose query text or
   sensitive literals in the report.
6. Classify findings and produce evidence-backed recommendations.
7. If `layout_mode` is `apply_approved`, apply only `cluster_by_auto` actions
   that pass the eligibility gates on `approved_tables`.

If a command or system table is unavailable, report `not_observable`; do not
translate missing evidence into `disabled`.

## Required checks

### Eligibility and table type

- Distinguish Unity Catalog managed, external, streaming, foreign, and view
  objects.
- Predictive optimization recommendations apply only to eligible Unity Catalog
  managed tables.
- Record Delta or Iceberg features and protocol compatibility before proposing
  a change.

### Liquid clustering

- Record `clusteringColumns` and `clusterByAuto`.
- Classify the table as `automatic`, `manual`, or `not_enabled`.
- Record static partition columns. Liquid clustering is not compatible with
  static partitioning or `ZORDER`.
- Do not call missing clustering a defect for a small, cold, or lookup table.
- Do not propose manual clustering keys without workload and cardinality
  evidence. Prefer automatic liquid clustering when eligible.
- Treat `clusterByAuto = true` as `already_applied`.

## Apply `CLUSTER BY AUTO`

Execute only when all of the following are true:

- `layout_mode` is `apply_approved`
- `allowed_layout_actions` contains `cluster_by_auto`
- the table is listed in `approved_tables`
- the table is Unity Catalog managed Delta
- `partitionColumns` is empty
- clustering is `not_enabled` (no liquid clustering keys and not already auto)
- no incompatible table feature or protocol blocks liquid clustering
- `MODIFY` permission is verified
- proposed SQL is exactly `ALTER TABLE <qualified> CLUSTER BY AUTO`

Skip and report rather than apply when:

- the table is partitioned, external, streaming, foreign, a view, or Iceberg-only
- clustering is already automatic
- clustering is already manual; converting from explicit keys needs review
- recent history shows `ZORDER`
- eligibility cannot be observed

Do not enable predictive optimization in the same action. If effective PO is
off or `not_observable`, apply clustering only if requested, then warn that
automatic key selection and clustering operations will not run until PO is
enabled. Do not run `OPTIMIZE ... FULL` after enabling clustering.

Apply one table at a time. Capture before-state and rollback SQL
(`CLUSTER BY NONE` when previously unclustered). Re-read `clusterByAuto`
after each statement. Treat an exact existing auto-clustered state as
`already_applied`. Persist every applied, failed, and already-applied action
to the ledger in [applied-actions-ledger.md](../applied-actions-ledger.md)
before reporting success.

### Predictive optimization

- Record the effective state and inheritance source.
- Inspect recent `COMPACTION`, `CLUSTERING`,
  `AUTO_CLUSTERING_COLUMN_SELECTION`, `ANALYZE`, and `VACUUM` evaluations when
  observable.
- Separate `enabled_but_not_yet_applied`, `successful`, `skipped`, and `failed`.
- Flag overlapping scheduled `OPTIMIZE`, `VACUUM`, or `ANALYZE` jobs for human
  review when predictive optimization already owns those operations.

### Partition and file layout

- Report table bytes, file count, average bytes per file, and partition columns.
- Treat average file size as a screening signal, not proof of a small-file
  problem. Use operation metrics or file distributions when available.
- Review static partitioning especially below 1 TB. If partition statistics are
  available, flag partitions below 1 GB as an evidence-backed concern.
- Inspect recent `OPTIMIZE` metrics: files added/removed, bytes added/removed,
  and file-size percentiles.
- Detect legacy `ZORDER` history and avoid recommending it together with liquid
  clustering.

### Maintenance and table features

- Check recent statistics collection, compaction, clustering, and vacuum
  activity.
- Report explicit file-size, auto-compaction, optimized-write, data-skipping,
  retention, and checkpoint properties that override platform defaults.
- Treat manual tuning as a review item, not automatically wrong.
- Recommend deletion vectors only for tables with material `DELETE`, `UPDATE`,
  or `MERGE` workloads and compatible readers.
- Warn before any retention change; preserve required time travel, recovery,
  streaming, and compliance windows.

## Finding rules

Every finding must contain:

- fully qualified table
- check name and status: `pass`, `opportunity`, `warning`, `failed`, or
  `not_observable`
- observed value and evidence source
- impact and confidence
- recommendation with prerequisites
- proposed SQL, when applicable, marked `not_executed` unless that exact
  statement was applied in this run

Use severity only when supported:

- `critical`: incompatible layout or maintenance failure with demonstrated risk
- `high`: repeated operational failure or strong workload-backed impact
- `medium`: actionable layout or maintenance opportunity
- `low`: informational or weak heuristic

Never mark a table healthy solely because a feature is enabled. Confirm recent
operations and outcomes when history is available.

## Output

Return:

- scope and capability summary
- per-table layout inventory
- liquid clustering and predictive optimization matrix
- maintenance history summary
- prioritized findings
- proposed SQL and expected effect
- applied, skipped, failed, already-applied, and review-required layout actions
- ledger SQL and notebook paths when any mutation was attempted
- unavailable evidence and permissions

Keep observations separate from recommendations. Quote all identifiers and make
all proposed changes individually reviewable.

## Invocation

```text
@data-layout-auditor
Tables: catalog.bronze.table_a, catalog.bronze.table_b
Layout mode: dry_run
Audit level: history
```

After review:

```text
@data-layout-auditor
Use the same tables as the previous dry run.
Layout mode: apply_approved
Allowed layout actions: cluster_by_auto
Approved tables:
- catalog.bronze.table_a
- catalog.bronze.table_b
```
