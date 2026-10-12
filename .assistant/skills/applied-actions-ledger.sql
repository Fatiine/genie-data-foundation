-- Genie Data Foundation applied-actions ledger
-- Append a new run section. Do not rewrite previous runs.
--
-- run_id:
-- started_at:
-- skill:
-- mode:
-- workspace:
-- operator:
-- table_scope:

-- ===== APPLIED =====
-- action_id:
-- target:
-- action:
-- action_kind: sql | api
-- status: applied
-- before:
-- after:
-- verified_at:

-- <executed SQL>;
-- API method/path:
-- Redacted request metadata:
-- Before JSON path:
-- After JSON path:
-- Before/after configuration hashes:

-- ===== SKIPPED / ALREADY_APPLIED / FAILED =====
-- action_id:
-- target:
-- action_kind: sql | api
-- action:
-- status:
-- reason:

-- ===== ROLLBACK (reverse order; do not run unless requested) =====
-- action_id:
-- target:
-- action_kind: sql | api

-- <rollback SQL>;
-- Rollback API payload path:
