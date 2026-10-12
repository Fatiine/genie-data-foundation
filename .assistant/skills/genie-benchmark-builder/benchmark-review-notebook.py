# Databricks notebook source
# MAGIC %md
# MAGIC # Genie benchmark review
# MAGIC
# MAGIC Review domain classifications and candidate SQL before publication.
# MAGIC This notebook does not publish benchmarks or execute candidate SQL.

# COMMAND ----------

dbutils.widgets.text("artifact_dir", "")
artifact_dir = dbutils.widgets.get("artifact_dir").rstrip("/")
if not artifact_dir:
    raise ValueError("Set artifact_dir to the generated benchmark artifact folder.")

# COMMAND ----------

domain_scope = (
    spark.read.option("multiline", "true")
    .json(f"{artifact_dir}/domain_scope.json")
)

display(
    domain_scope.select(
        "question_id",
        "intent_id",
        "question",
        "domain_status",
        "confidence",
        "answer_grain",
        "review_status",
        "missing_requirements",
        "rationale",
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Questions requiring clarification or missing data

# COMMAND ----------

display(
    domain_scope.where("domain_status <> 'in_scope'").select(
        "question_id",
        "question",
        "domain_status",
        "missing_requirements",
        "rationale",
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ground-truth candidates
# MAGIC
# MAGIC Review SQL in `benchmark_review.sql`. Confirm interpretation, sources,
# MAGIC joins, filters, time semantics, aggregation, grain, and result schema.
# MAGIC Record approvals in the generated review artifact; do not edit the live
# MAGIC Genie Agent from this notebook.

# COMMAND ----------

display(
    domain_scope.where("domain_status = 'in_scope'").select(
        "question_id",
        "question",
        "required_sources",
        "required_columns",
        "required_joins",
        "required_measures",
        "filters",
        "time_semantics",
        "answer_grain",
        "candidate_sql",
        "validation",
        "review_status",
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Approval rules
# MAGIC
# MAGIC A benchmark can be published only when:
# MAGIC
# MAGIC - `domain_status` is `in_scope`
# MAGIC - SQL parsing, explain, and execution passed
# MAGIC - the reviewer explicitly set `review_status` to `approved`
# MAGIC - the question ID is supplied in `approved_question_ids`
# MAGIC
# MAGIC Publishing is performed by `@genie-benchmark-builder` in
# MAGIC `apply_approved` mode, with before/after backups and rollback metadata.
