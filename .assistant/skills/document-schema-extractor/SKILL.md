---
name: document-schema-extractor
description: Extracts evidence-backed table, column, key, relationship, and metric metadata from vendor PDFs and other data dictionaries. Use when onboarding documentation into Unity Catalog or preparing semantic metadata from documents.
---

# Document schema extractor

Turn one or more documents into structured semantic evidence. Do not update Unity Catalog in this skill.

## Required inputs

- `document_paths`: UC Volume paths, workspace file paths, or accessible local paths.
- Optional `table_hints`: fully qualified table names or source names expected in the documents.
- Optional `output_table`: Delta table for extracted evidence. If omitted, return a temporary view or JSON artifact.

If an input is missing, ask only for that input. Never guess a document path.

## Workflow

1. Record each document's path, filename, size, and content hash.
2. Parse native and scanned documents:
   - In Databricks, prefer `ai_parse_document` over files read as binary from a UC Volume.
   - For local text PDFs, run `scripts/extract_pdf.py`.
   - If extraction returns little text or no tables, report `OCR_REQUIRED`; do not interpret an empty result as absence of metadata.
3. Locate likely schema sections using headings such as data dictionary, schema, fields, files, tables, keys, formulas, methodology, and index.
4. Extract evidence using the contract in [evidence-contract.md](evidence-contract.md).
5. Preserve source wording in `source_excerpt`. Normalize names only in separate normalized fields.
6. Deduplicate repeated appendix/index entries in favor of the most detailed definition, while retaining all evidence locations.
7. Emit extraction statistics and unresolved ambiguities.

## Extraction rules

- A table or field must have a document citation: document path, 1-based page, and excerpt.
- Record a PK or FK as `declared` only when the document explicitly labels it. Otherwise use `inferred` and explain the inference.
- Keep composite-key column order.
- Do not convert examples into constraints.
- Do not infer a relationship solely because two columns have the same name.
- Keep formulas verbatim and separately provide a normalized SQL candidate.
- Record grain, time frequency, currency behavior, restatement behavior, units, and additive behavior when stated.
- Distinguish physical source files, database tables, views, packages, and conceptual entities.
- Set confidence from evidence quality, not model certainty.

## Confidence

- `1.00`: explicit declaration in a structured dictionary row.
- `0.90-0.99`: explicit prose tied unambiguously to one object.
- `0.75-0.89`: strong contextual inference requiring catalog validation.
- `<0.75`: review only; never eligible for automatic publication.

## Databricks-native parsing

For UC Volume documents, use this pattern and persist the returned VARIANT before extraction:

```sql
SELECT
  path,
  ai_parse_document(content, map('version', '2.0')) AS parsed_document
FROM READ_FILES('/Volumes/<catalog>/<schema>/<volume>/<path>', format => 'binaryFile');
```

For files over the service page limit, parse explicit page ranges and merge by page number. Do not silently omit pages.

## Output

Return:

1. Evidence records following [evidence-contract.md](evidence-contract.md).
2. Document coverage: pages parsed, failed pages, and extraction method.
3. Counts by object and assertion type.
4. Ambiguities and conflicts.
5. A concise handoff suitable for `catalog-metadata-publisher` and `semantic-view-builder`.

Never publish comments, tags, constraints, views, or metrics from this skill.
