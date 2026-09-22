# Synthetic customer onboarding example

This example uses fictional assets. Do not commit real customer or vendor documentation.

## Scenario

A customer has two bronze tables:

- `acme.bronze.orders`
- `acme.bronze.customers`

Their data dictionary is stored at:

- `/Volumes/acme/governance/documents/commerce_dictionary.pdf`

The semantic assets should be created in `acme.semantic`.

## Step 1: Dry run

```text
@semantic-onboarding
Documents:
- /Volumes/acme/governance/documents/commerce_dictionary.pdf
Tables:
- acme.bronze.orders
- acme.bronze.customers
Target schema: acme.semantic
Mode: dry_run
Create: comments, tags, relationships, views, metric views
Allowed tags: source_system, business_domain, data_frequency
```

Review:

- document pages successfully parsed
- table and column matches
- proposed descriptions and tags
- candidate PK/FK integrity checks
- join cardinality and expected grain
- metric formulas and aggregation behavior
- existing metadata conflicts
- generated SQL, YAML, and rollback statements

## Step 2: Apply safe changes

```text
@semantic-onboarding
Use the same documents, tables, target schema, and allowed tags as the previous dry run.
Mode: auto_apply_high_confidence
Apply only proposals that meet the skill's automatic-publication policy.
Return all ambiguous proposals for review.
```

## Step 3: Review the result

Confirm that:

- existing curated metadata was preserved
- primary and foreign keys are described as informational
- created views are in `acme.semantic`
- metric results match documented examples
- the run report contains source citations and rollback SQL
