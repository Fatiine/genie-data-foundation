# Domain and benchmark contract

Persist one record per submitted question in `domain_scope.json`.

## Required question fields

```json
{
  "question_id": "32-character hexadecimal stable id",
  "intent_id": "stable intent group id",
  "question": "Original user wording",
  "normalized_question": "Normalized comparison text",
  "domain_status": "in_scope",
  "confidence": 0.98,
  "rationale": "Why the classification is supported",
  "required_sources": ["catalog.schema.table"],
  "required_columns": ["catalog.schema.table.column"],
  "required_joins": [],
  "required_measures": [],
  "filters": [],
  "time_semantics": null,
  "answer_grain": "one row",
  "evidence": [],
  "missing_requirements": [],
  "candidate_sql": "SELECT ...",
  "validation": {},
  "review_status": "pending",
  "reviewer": null,
  "reviewed_at": null
}
```

`domain_status` must be `in_scope`, `partially_answerable`, `ambiguous`, or
`out_of_scope`. `review_status` must be `pending`, `approved`, or `rejected`.
Reject confidence outside `[0, 1]`.

Evidence records contain:

- `kind`: catalog metadata, document citation, constraint, metric definition,
  validated relationship, or query validation
- `source`: fully qualified object or document path
- `detail`: concise evidence without sensitive values

## SQL validation

For an `in_scope` candidate, retain:

```json
{
  "parse_status": "passed",
  "explain_status": "passed",
  "execution_status": "passed",
  "validated_at": "timestamp",
  "warehouse_id": "warehouse id",
  "referenced_objects": ["catalog.schema.table"],
  "result_columns": [
    {"name": "total_revenue", "type": "DECIMAL(38,2)"}
  ],
  "row_count": 1,
  "result_signature": "sha256:...",
  "warnings": []
}
```

The signature must be non-reversible and stable for the validated result
representation. Never persist raw result rows in this contract.

An empty result is not automatically incorrect, but it requires review because
the benchmark service cannot distinguish a valid empty answer from ineffective
ground truth without business evidence.

## Genie benchmark object

Only approved `in_scope` records become benchmark objects:

```json
{
  "id": "32-character hexadecimal stable id",
  "question": ["What is average order value?"],
  "answer": [
    {
      "format": "SQL",
      "content": [
        "SELECT AVG(order_amount) AS average_order_value\n",
        "FROM catalog.schema.orders"
      ]
    }
  ]
}
```

Split SQL into ordered content strings without changing its meaning. Keep each
question phrasing as its own benchmark object. Equivalent phrasings share the
same approved SQL and `intent_id` in the review artifact.

## Domain summary

`run_report.json` includes:

- input hash and `run_id`
- resolved source scope and existing agent sources
- count by domain and review status
- intent coverage and paraphrase counts
- recommended minimal data sources
- unsupported data and semantic gaps
- duplicate/conflict findings
- artifact paths
- publication and evaluation summaries

Do not claim percentage coverage without stating the denominator: all submitted
questions, unique intents, or approved benchmark questions.
