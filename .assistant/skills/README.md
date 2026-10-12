# Genie Data Foundation skills

Project-staged Genie Code skills for document-driven Unity Catalog enrichment.

## Skills

- `@semantic-onboarding`: complete workflow
- `@document-schema-extractor`: document evidence only
- `@catalog-semantic-profiler`: read-only catalog and data checks
- `@data-layout-auditor`: liquid clustering, predictive optimization, and Delta layout audit; optional approved `CLUSTER BY AUTO`
- `@catalog-metadata-publisher`: comments, tags, and informational constraints
- `@semantic-view-builder`: standard views and metric views
- `@genie-benchmark-builder`: question-driven domain scoping, reviewed ground-truth SQL, benchmark publication, and evaluation

Start with `dry_run`. Each skill accepts document/table inputs at invocation time, so no vendor or catalog names are hard-coded.

Applied SQL and API mutations are written to `applied_actions.sql` and `applied_actions.py` under `/Workspace/.assistant/runs/<run_id>/`, or to `ledger_path` when supplied.

## Install in Databricks

After review, copy each skill directory into one of:

- Workspace: `Workspace/.assistant/skills/`
- User: `/Users/<username>/.assistant/skills/`

Keep the directory structure intact. Start a new Genie Code chat after installation; use an `@` mention to force a specific skill.

## Example

```text
@semantic-onboarding
Document: /Volumes/vendor/docs/data_dictionary.pdf
Tables: catalog.bronze.table_a, catalog.bronze.table_b
Target schema: catalog.semantic
Mode: dry_run
```

The workflow auto-applies only after `Mode: auto_apply_high_confidence` is explicitly selected. Ambiguous mappings and formulas remain proposals.
