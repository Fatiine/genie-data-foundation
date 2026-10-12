# Applied-actions ledger

When any skill executes mutating SQL, persist an append-only ledger before
reporting success. Dry runs do not write a ledger.

## Destination

Prefer an explicit `ledger_path`. Otherwise create:

```text
/Workspace/.assistant/runs/<run_id>/applied_actions.sql
/Workspace/.assistant/runs/<run_id>/applied_actions.py
```

If the caller supplies a Unity Catalog Volume directory, write the same two
filenames there. Do not overwrite an existing file; append a new run section.
If workspace write fails, keep the full ledger in the response and mark
`ledger_status: not_persisted`.

## Required SQL file

Use [applied-actions-ledger.sql](applied-actions-ledger.sql). Each applied
statement needs:

- `run_id`, skill, mode, timestamp, operator
- fully qualified target
- action name and proposal id
- before/after state
- executed SQL
- verification result
- rollback SQL

Put rollback statements in reverse apply order in a commented `ROLLBACK`
section. Never execute rollback unless the caller requests it.

## Optional notebook

Use [applied-actions-notebook.py](applied-actions-notebook.py) so operators can
open the same run in Databricks. The notebook must match the SQL file; the SQL
file is the source of truth.

## Rules

- Write the ledger after each successful statement, or atomically after the
  apply batch if that is safer.
- Include failed attempts with `status: failed` and the error; do not put
  failed SQL in the executable apply section.
- `already_applied` and skipped actions are comments only.
- Return the ledger path in the skill summary.
