# Genie Data Foundation skills

Project-staged Genie Code skills for document-driven Unity Catalog enrichment.

## Skills

- `@semantic-onboarding`: complete workflow
- `@document-schema-extractor`: document evidence only
- `@catalog-semantic-profiler`: read-only catalog and data checks
- `@catalog-metadata-publisher`: comments, tags, and informational constraints
- `@semantic-view-builder`: standard views and metric views

Start with `dry_run`. Each skill accepts document/table inputs at invocation time, so no vendor or catalog names are hard-coded.

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
