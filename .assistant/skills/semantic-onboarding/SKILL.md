---
name: semantic-onboarding
description: Orchestrates document extraction, Unity Catalog profiling, metadata enrichment, relationship validation, and semantic or metric view creation for any supplied documents and table scope. Use for end-to-end onboarding of vendor or internal data into Genie-ready semantics.
---

# Semantic onboarding

Run an evidence-first semantic onboarding workflow. This skill coordinates the same phases exposed by `document-schema-extractor`, `catalog-semantic-profiler`, `catalog-metadata-publisher`, and `semantic-view-builder`.

## Invocation

Collect these inputs:

- `document_paths`: one or more PDF/document paths.
- `table_scope`: fully qualified table list or one bounded catalog/schema pattern.
- `target_schema`: destination for generated views and metric views.
- `mode`: default `dry_run`; allowed values are `dry_run`, `apply_approved`, and `auto_apply_high_confidence`.

Optional: table name mappings, tag allow-list, output/control schema, maximum table count, profile limits, naming prefix, and desired asset types.

Confirm the resolved source table list and target schema before any mutation. Do not accept an unbounded metastore-wide scope.

## Phases

### 1. Preflight

- Verify document readability, source permissions, target privileges, supported compute/runtime, and Delta eligibility for constraints.
- Generate `run_id`; hash documents and inputs.
- Capture the current metadata state.

### 2. Extract document evidence

- Follow the rules of `document-schema-extractor`.
- Preserve page-level citations and explicit-versus-inferred status.
- Stop if critical pages fail extraction.

### 3. Profile the catalog

- Follow `catalog-semantic-profiler`.
- Resolve exact source objects and inspect existing metadata.
- Run full-data key/integrity checks only for shortlisted candidates.

### 4. Reconcile and propose

- Match document objects to catalog objects.
- Score every mapping and action.
- Materialize a run report following [run-contract.md](run-contract.md).
- Separate eligible, review-required, conflict, invalid, and already-applied actions.

### 5. Publish metadata

- Follow `catalog-metadata-publisher`.
- In `dry_run`, execute no DDL.
- In `apply_approved`, apply only proposal IDs supplied by the user.
- In `auto_apply_high_confidence`, apply only actions passing all type-specific thresholds.

### 6. Build semantic assets

- Follow `semantic-view-builder`.
- Build views only in `target_schema`.
- Validate join grain and formulas before creation.
- Never replace an object not owned by this workflow.

### 7. Verify and report

- Re-read metadata and query created assets.
- Record before/after state, validation results, definition hashes, and rollback SQL.
- Summarize coverage and unresolved review items.

## Automatic-apply policy

Automatic means no per-action confirmation after the caller selects `auto_apply_high_confidence`; it does not relax validation.

- Comments/tags require confidence `>= 0.95`, exact unambiguous target, explicit evidence, and no curated conflict.
- PK/FK publication requires explicit document declaration at confidence `1.00` plus complete integrity checks. Never alter nullability automatically.
- Views/metric views require valid syntax, successful preview, validated joins, explicit target schema, and a free or workflow-owned target name.
- Formula ambiguity, unknown aggregation, uncertain grain, failed OCR, sampled-only key checks, or conflicting documentation always requires review.

## Failure behavior

- Fail closed: a missing permission, partial document parse, timeout, or inconclusive validation lowers eligibility; it never raises confidence.
- Continue independent actions when safe, but skip dependents of failed actions.
- Do not roll back successful unrelated metadata automatically. Provide precise rollback SQL.
- Never expose document content or sampled data beyond the authorized workspace.

## Final response

Keep the summary short:

- documents/pages and tables covered
- actions applied, proposed, skipped, conflicted, and failed
- views/metric views created
- validations performed
- location of the detailed report and rollback SQL
- next approvals required

For examples and the run record, see [run-contract.md](run-contract.md).
