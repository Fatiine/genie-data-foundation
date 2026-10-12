-- Genie benchmark ground-truth review
-- Generated from benchmark-contract.md. Do not publish from this file.
--
-- run_id: <run_id>
-- generated_at: <timestamp>
-- question_id: <stable id>
-- intent_id: <intent id>
-- question: <original question>
-- domain_status: in_scope
-- required_sources: <fully qualified sources>
-- answer_grain: <grain>
-- evidence: <concise evidence>
-- validation_status: <status>
-- result_schema: <column names and types>
-- result_row_count: <count>
-- result_signature: sha256:<digest>
-- review_status: pending
-- reviewer:
-- reviewed_at:

-- Candidate SQL starts below. It must be one read-only SELECT or WITH statement.
SELECT
  '<replace with generated ground-truth SQL>' AS review_placeholder;

-- Review checklist:
-- [ ] The question has one unambiguous interpretation.
-- [ ] Tables, columns, joins, and measures are correct.
-- [ ] Filters and time semantics match the wording.
-- [ ] Aggregation and output grain are correct.
-- [ ] Output columns are stable and appropriately named.
-- [ ] SQL does not expose sensitive row-level data.
-- [ ] Result shape and signature were validated.
--
-- Set review_status to approved only after all checks pass.
