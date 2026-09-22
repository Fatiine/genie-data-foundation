# Evidence contract

Produce one record per assertion. JSON, a DataFrame, or a Delta table is acceptable if these fields are retained.

## Required fields

| Field | Meaning |
|---|---|
| `document_id` | Stable content hash |
| `document_path` | Original path |
| `page_number` | 1-based page number |
| `source_excerpt` | Verbatim evidence |
| `object_type` | `table`, `column`, `primary_key`, `foreign_key`, `relationship`, `metric`, `formula`, or `business_rule` |
| `source_table_name` | Name as printed |
| `source_column_name` | Name as printed, when applicable |
| `attribute` | Asserted property such as `description`, `datatype`, `primary_key`, or `formula` |
| `value_json` | Structured asserted value |
| `evidence_kind` | `declared` or `inferred` |
| `confidence` | Decimal from 0 through 1 |
| `rationale` | Why this assertion was extracted |

## Optional semantic fields

- `normalized_table_name`, `normalized_column_name`
- `referenced_table_name`, `referenced_column_names`
- `column_ordinal`, `key_ordinal`
- `datatype`, `nullable`, `unit`, `currency`
- `grain`, `frequency`, `aggregation`, `additivity`
- `formula_verbatim`, `formula_sql_candidate`
- `synonyms`, `classification_tags`
- `effective_version`, `package`, `region`

## Example

```json
{
  "document_id": "sha256:...",
  "document_path": "/Volumes/vendor/docs/guide.pdf",
  "page_number": 30,
  "source_excerpt": "Primary Key – FSYM_ID",
  "object_type": "primary_key",
  "source_table_name": "FF_SEC_MAP",
  "source_column_name": null,
  "attribute": "primary_key",
  "value_json": {"columns": ["FSYM_ID"]},
  "evidence_kind": "declared",
  "confidence": 1.0,
  "rationale": "Explicit primary-key label in the table dictionary."
}
```

## Quality checks

- Reject records without a page and excerpt.
- Reject confidence outside `[0, 1]`.
- Reject keys with empty column arrays.
- Flag contradictory assertions for the same object and attribute.
- Preserve multiple citations for corroborating evidence.
