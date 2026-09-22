# Genie Data Foundation

Reusable Genie Code skills that transform documented data assets and base tables into a governed Unity Catalog foundation: metadata, relationships, semantic views, and metrics.

The project helps data teams go from bronze or base tables and data dictionaries through catalog curation to a semantic layer.

## What it does

```text
Documents + Unity Catalog tables
              |
              v
   Prepare the data foundation
              |
              v
  Match, validate, and curate catalog assets
              |
              v
Comments, tags, PK/FK, views,
and metric views (semantic layer)
```

The workflow retains document-page evidence, validates key integrity and join cardinality, protects existing curated metadata, and supports dry runs before applying changes.

## Included skills

| Skill | Purpose |
|---|---|
| `@semantic-onboarding` | Runs the complete document-to-semantic-layer workflow |
| `@document-schema-extractor` | Extracts tables, fields, definitions, keys, formulas, and citations |
| `@catalog-semantic-profiler` | Profiles Unity Catalog metadata and validates key candidates |
| `@catalog-metadata-publisher` | Publishes comments, tags, and informational PK/FK constraints |
| `@semantic-view-builder` | Builds standard views and Unity Catalog metric views |

## Safety model

- Defaults to `dry_run`.
- Applies metadata automatically only for exact, high-confidence matches.
- Never overwrites conflicting curated comments or governed tags automatically.
- Requires complete duplicate, null, and orphan checks before publishing keys.
- Treats Databricks PK/FK constraints as informational, not enforced.
- Never replaces a customer-owned view.
- Sends ambiguous formulas, grains, joins, and mappings for review.

## Installation

Copy the skill folders from [`.assistant/skills/`](.assistant/skills/) into one of these Databricks workspace locations:

- Workspace skills: `Workspace/.assistant/skills/`
- Personal skills: `/Users/<username>/.assistant/skills/`

Start a new Genie Code conversation after installation.

## Quick start

Store the source documents in a Unity Catalog Volume, then invoke:

```text
@semantic-onboarding
Documents:
- /Volumes/customer_data/documentation/data_dictionary.pdf
Tables:
- customer_catalog.bronze.orders
- customer_catalog.bronze.customers
Target schema: customer_catalog.semantic
Mode: dry_run
Create: comments, tags, relationships, views, metric views
```

Review the generated evidence and proposals. When the mapping is correct, rerun with:

```text
Mode: auto_apply_high_confidence
```

## Document support

Databricks `ai_parse_document` supports PDF, DOC/DOCX, PPT/PPTX, JPG/JPEG, PNG, and TIFF inputs. The included local fallback supports text-based PDFs and flags likely scanned documents that require OCR.

Spreadsheet, CSV, HTML, email, and proprietary documentation formats require additional extraction adapters.

## Prerequisites

- Databricks workspace with Genie Code and Unity Catalog
- Source documents accessible to Genie Code, preferably in UC Volumes
- A SQL warehouse or compatible cluster
- `SELECT` on source tables
- Relevant `USE CATALOG`, `USE SCHEMA`, `MODIFY`, and governed-tag permissions
- `CREATE TABLE` in the target schema for metric views
- Delta/Unity Catalog tables for informational PK/FK constraints
- Databricks Runtime 16.4+ for metric views; 17.3+ recommended for YAML 1.1 features

See [the complete skill documentation](docs/genie-semantic-skills.md) for individual prerequisites and limitations.

## Validation

Run the standard-library test suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .assistant/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 .assistant/tests/validate_skills.py
```

## Customer data and licensing

Do not commit vendor documents, customer schemas, extracted content, credentials, or generated reports. The repository excludes common document formats by default. Use synthetic examples when extending or testing the skills.

Licensed under the [Apache License 2.0](LICENSE).
