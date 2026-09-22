# Publication proposal contract

Each proposed change must include:

```json
{
  "proposal_id": "stable-hash",
  "run_id": "uuid",
  "target_object": "catalog.schema.table.column",
  "action_type": "column_comment",
  "desired_value": "Vendor description",
  "current_value": null,
  "confidence": 0.98,
  "match_method": "exact_normalized_name",
  "evidence": [
    {
      "document_path": "/Volumes/vendor/docs/guide.pdf",
      "page_number": 30,
      "source_excerpt": "..."
    }
  ],
  "validations": [],
  "decision": "eligible",
  "decision_reason": "Unambiguous column match with explicit dictionary description",
  "sql": "COMMENT ON COLUMN ...",
  "rollback_sql": "COMMENT ON COLUMN ... IS NULL"
}
```

## Action types

- `table_comment`
- `column_comment`
- `table_tag`
- `column_tag`
- `primary_key`
- `foreign_key`

## Decisions

- `eligible`: may run under the selected mode.
- `review_required`: useful proposal that fails automatic thresholds.
- `conflict`: current curated metadata disagrees.
- `invalid`: missing object, incompatible type, or failed integrity check.
- `already_applied`: desired state already exists.

Compute `proposal_id` from the target, action, desired value, and evidence hash so reruns are idempotent.
