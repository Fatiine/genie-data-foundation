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
-- status: applied
-- before:
-- after:
-- verified_at:

-- <executed SQL>;

-- ===== SKIPPED / ALREADY_APPLIED / FAILED =====
-- action_id:
-- target:
-- action:
-- status:
-- reason:

-- ===== ROLLBACK (reverse order; do not run unless requested) =====
-- action_id:
-- target:

-- <rollback SQL>;
