# Databricks notebook source
# MAGIC %md
# MAGIC # Applied actions ledger
# MAGIC
# MAGIC - `run_id`:
# MAGIC - `skill`:
# MAGIC - `mode`:
# MAGIC - `started_at`:
# MAGIC - SQL source of truth: `applied_actions.sql` in the same folder
# MAGIC
# MAGIC Cells below describe the SQL or API actions that succeeded. API actions
# MAGIC reference redacted request metadata and before/after JSON artifacts.
# MAGIC Rollback is in a later section and must not be run unless requested.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Applied
# MAGIC
# MAGIC For API actions, record method/path, response status, before/after
# MAGIC configuration hashes, and backup paths. Never include credentials.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- action_id:
# MAGIC -- target:
# MAGIC -- before:
# MAGIC -- after:
# MAGIC SELECT 'replace-with-applied-statement';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Rollback (do not run unless requested)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- reverse order
# MAGIC SELECT 'replace-with-rollback-statement';
