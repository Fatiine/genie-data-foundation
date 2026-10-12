# Genie Agent API templates

Use workspace OAuth and the `genie` API scope. Never log bearer tokens. Confirm
the current REST schema from the workspace before publication.

## Read the current agent

```http
GET /api/2.0/genie/spaces/{space_id}
```

Persist the full response as `genie_space.before.json`. Parse
`serialized_space` as JSON but retain the original string, top-level fields,
`etag`, and a SHA-256 configuration hash.

## Merge approved benchmarks

Modify only:

```text
serialized_space.benchmarks.questions
```

Merge rules:

1. Preserve all existing questions and unrelated configuration.
2. Preserve an existing ID when question and SQL are identical.
3. Treat identical ID and content as `already_applied`.
4. Block an ID with different question or answer.
5. Block a normalized duplicate with conflicting SQL.
6. Do not delete or rewrite an existing benchmark implicitly.
7. Serialize using the live configuration version.

## Update the agent

```http
PATCH /api/2.0/genie/spaces/{space_id}
If-Match: {etag}
Content-Type: application/json

{
  "title": "{unchanged live title}",
  "description": "{unchanged live description}",
  "warehouse_id": "{unchanged live warehouse id}",
  "parent_path": "{unchanged live parent path}",
  "serialized_space": "{complete escaped merged configuration}"
}
```

The update replaces the serialized configuration. Never send a partial
`serialized_space`.

If the endpoint does not support `If-Match`, re-fetch immediately before
`PATCH` and compare the live `etag` or configuration hash with the captured
value. Stop on mismatch.

## Verify and roll back

After update:

```http
GET /api/2.0/genie/spaces/{space_id}
```

Persist `genie_space.after.json`. Verify every approved benchmark ID, question,
and SQL answer. The rollback payload is a full update using the before-state
top-level fields and `serialized_space`. Never execute rollback automatically.

Record request metadata, response status, before/after hashes, verification,
and rollback path in the applied-actions ledger. Redact tokens and sensitive
headers.

## Start a baseline evaluation

The public endpoint runs chat-mode evaluations:

```http
POST /api/2.0/genie/spaces/{space_id}/eval-runs
Content-Type: application/json

{
  "benchmark_question_ids": [
    "{new question id}"
  ]
}
```

Run only the newly published IDs unless the caller explicitly requests all
benchmarks.

## Read evaluation results

```http
GET /api/2.0/genie/spaces/{space_id}/eval-runs/{eval_run_id}/results
GET /api/2.0/genie/spaces/{space_id}/eval-runs/{eval_run_id}/results/{result_id}
```

Follow pagination. Persist IDs and summaries, not sensitive response rows.
Capture:

- run status and completion counts
- correct and needs-review counts
- per-question assessment
- assessment reasons such as missing rows, columns, filters, joins, or
  aggregation

Evaluation failure does not imply publication failure. Report the two statuses
separately.
