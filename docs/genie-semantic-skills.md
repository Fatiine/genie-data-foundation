# Genie Semantic Skills

A vendor-neutral suite of Genie Code agent skills that turn data documentation (such as vendor PDFs and data dictionaries) into governed Unity Catalog metadata, relationships, and semantic assets.

The suite is one orchestrator plus four specialist skills. Each specialist is callable on its own; the orchestrator runs them end to end.

## Skills

### 1. `@semantic-onboarding` (orchestrator)

Runs the complete workflow:

1. Reads the supplied documents.
2. Scans the selected Unity Catalog tables.
3. Matches documented tables/columns to catalog objects.
4. Proposes or applies descriptions, tags, primary keys, and foreign keys.
5. Creates semantic views and metric views.
6. Produces validation results and rollback SQL.

Prerequisites:
- Document paths
- Explicit table list or a bounded catalog/schema pattern
- Target schema for generated views
- Unity Catalog access
- SQL warehouse or cluster
- `SELECT` on source tables
- `USE CATALOG`, `USE SCHEMA`, and metadata modification permissions
- `CREATE TABLE` in the target schema for metric views

Example:

```text
@semantic-onboarding
Documents: /Volumes/vendor/docs/guide.pdf
Tables: catalog.bronze.table_a, catalog.bronze.table_b
Target schema: catalog.semantic
Mode: dry_run
```

### 2. `@document-schema-extractor`

Reads documentation and extracts:

- Tables and columns
- Descriptions and datatypes
- Declared primary keys and foreign keys
- Relationships
- Formulas and metric definitions
- Grain, frequency, currency, and restatement rules
- Document page and exact source excerpt

Does not modify Unity Catalog.

Prerequisites:
- Accessible document path
- Preferably documents stored in a Unity Catalog Volume
- Access to `ai_parse_document`, or local Python with `pypdf` / `pdftotext`

### 3. `@catalog-semantic-profiler`

Scans the actual Unity Catalog tables and collects:

- Columns and datatypes
- Existing comments and tags
- Existing PK/FK/unique constraints
- Candidate keys
- Null and duplicate checks
- Foreign-key orphan checks
- Possible table grain and relationships

Read-only.

Prerequisites:
- Unity Catalog tables
- Explicit table list or a limited catalog/schema pattern
- `USE CATALOG`, `USE SCHEMA`, and `SELECT`
- Access to the relevant `INFORMATION_SCHEMA`
- Compute for optional data profiling

Two profiling levels:
- `metadata`: catalog metadata only
- `bounded_data`: also validates candidate keys and relationships using data

### 4. `@catalog-metadata-publisher`

Publishes validated metadata:

- Table comments
- Column comments
- Table and column tags
- Informational primary keys
- Informational foreign keys

Protects existing customer metadata and defaults to `dry_run`.

Prerequisites:
- Output from the document extractor
- Output from the catalog profiler
- Unity Catalog-managed objects
- `MODIFY` permission on source tables
- Permission to assign governed tags, where applicable
- Delta tables for PK/FK constraints
- Databricks Runtime 15.2+ recommended for GA PK/FK support

Note: Databricks PK and FK constraints are informational, not enforced.

Automatic publication requires:
- Exact, unambiguous metadata match
- Confidence of at least 0.95 for comments/tags
- Explicitly declared keys
- Zero PK nulls/duplicates
- Zero FK orphans
- Compatible datatypes

### 5. `@semantic-view-builder`

Creates analytics-friendly assets:

- Standard SQL views
- Joined semantic views
- Unity Catalog metric views
- Dimensions, measures, synonyms, comments, and formats
- Validated many-to-one relationships

Prerequisites:
- Validated source tables and relationships
- Explicit target schema
- `SELECT` on source objects
- `USE CATALOG` and `USE SCHEMA`
- `CREATE TABLE` in the target schema
- SQL warehouse or compatible cluster
- Runtime 16.4+ for metric views; 17.3+ recommended for the YAML 1.1 features used by the templates

Does not assume every numeric field should be summed. Metric formulas and aggregation behavior must be documented or explicitly approved.

## Document support

With Databricks `ai_parse_document`:
- PDF
- DOC / DOCX
- PPT / PPTX
- JPG / JPEG
- PNG
- TIFF

Local fallback (`document-schema-extractor/scripts/extract_pdf.py`):
- Text-based PDF only
- Detects likely scanned PDFs but does not perform OCR

Not currently supported without additional adapters:
- Excel, CSV, HTML, email, and proprietary formats

Document quality matters: unclear or poorly structured documentation produces review proposals instead of automatic metadata.

## Overall limitations

- Works best with formal data dictionaries and schema guides.
- Scanned documents need Databricks document parsing/OCR.
- Ambiguous relationships and formulas require review.
- Excel and CSV documentation are not currently supported by the extractor.
- The skills are staged locally; they must be copied to `Workspace/.assistant/skills/` before Genie Code can use them.

## Repository layout

```
.assistant/
  skills/
    semantic-onboarding/
    document-schema-extractor/
    catalog-semantic-profiler/
    catalog-metadata-publisher/
    semantic-view-builder/
    README.md
  tests/
    validate_skills.py
    test_policy_contracts.py
docs/
  genie-semantic-skills.md
```
