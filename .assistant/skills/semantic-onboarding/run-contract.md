# Invocation and run contract

## Recommended prompt

```text
@semantic-onboarding
Documents:
- /Volumes/vendor_docs/guides/fundamentals.pdf
Tables:
- finance_bronze.factset.ff_basic_af
- finance_bronze.factset.ff_sec_coverage
Target schema: finance_semantic.factset
Mode: dry_run
Create: comments, tags, relationships, views, metric views
```

Use `Mode: auto_apply_high_confidence` only after a successful dry run establishes the expected mappings and target schema.

## Pattern prompt

```text
@semantic-onboarding
Use all PDFs under /Volumes/vendor_docs/guides/factset/.
Resolve tables matching finance_bronze.factset.ff_* with a maximum of 75 tables.
Create semantic assets in finance_semantic.factset.
Mode: auto_apply_high_confidence.
Allowed tags: source_system, business_domain, data_frequency, currency_behavior.
```

## Run record

Persist or return:

```json
{
  "run_id": "uuid",
  "started_at": "timestamp",
  "mode": "dry_run",
  "input_hash": "sha256:...",
  "documents": [],
  "resolved_tables": [],
  "runtime_capabilities": {},
  "extraction_summary": {},
  "catalog_snapshot": {},
  "proposals": [],
  "applied_actions": [],
  "validation_results": [],
  "created_assets": [],
  "conflicts": [],
  "failures": [],
  "rollback_sql": [],
  "status": "completed_with_review"
}
```

## Idempotency

- Derive proposal IDs from normalized target, action, desired state, and evidence hash.
- Compare desired state with live state before execution.
- Treat an exact existing state as `already_applied`.
- Store a definition hash for generated views.
- Replace a generated view only when ownership is proven and the new definition was validated.

## Suggested statuses

- `completed`
- `completed_with_review`
- `dry_run_complete`
- `blocked`
- `failed`
