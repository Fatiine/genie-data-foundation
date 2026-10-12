#!/usr/bin/env python3
"""Regression tests for safety and idempotency requirements."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def read_skill(name: str, resource: str = "SKILL.md") -> str:
    return (SKILLS / name / resource).read_text(encoding="utf-8")


class PolicyContractTests(unittest.TestCase):
    def test_publisher_has_strict_auto_apply_thresholds(self) -> None:
        policy = read_skill("catalog-metadata-publisher")
        self.assertIn("confidence `>= 0.95`", policy)
        self.assertIn("explicit declared evidence at `1.00`", policy)
        self.assertIn("full-data orphan count is zero", policy)
        self.assertIn("Never automatically:", policy)
        self.assertIn("change column nullability", policy)
        self.assertIn("publish an inferred PK/FK", policy)

    def test_existing_customer_metadata_is_protected(self) -> None:
        publisher = read_skill("catalog-metadata-publisher")
        builder = read_skill("semantic-view-builder")
        self.assertIn("no conflicting curated comment", publisher)
        self.assertIn("Never replace an unowned object", builder)

    def test_dry_run_is_default_and_non_mutating(self) -> None:
        publisher = read_skill("catalog-metadata-publisher")
        orchestrator = read_skill("semantic-onboarding")
        self.assertIn("Default to `dry_run`", publisher)
        self.assertIn("In `dry_run`, execute no DDL", orchestrator)

    def test_composite_and_invalid_fk_checks_are_required(self) -> None:
        profiler = read_skill("catalog-semantic-profiler", "sql-templates.md")
        publisher = read_skill("catalog-metadata-publisher")
        self.assertIn("STRUCT(col1, col2, ...)", profiler)
        self.assertIn("full-data orphan count is zero", publisher)
        self.assertIn("types and column order match", publisher)

    def test_layout_auditor_is_read_only_and_evidence_based(self) -> None:
        auditor = read_skill("data-layout-auditor")
        templates = read_skill("data-layout-auditor", "sql-templates.md")
        orchestrator = read_skill("semantic-onboarding")
        self.assertIn("Default `layout_mode` is", auditor)
        self.assertIn("`dry_run`", auditor)
        self.assertIn("not_observable", auditor)
        self.assertIn("clusteringColumns", auditor)
        self.assertIn("Predictive Optimization", templates)
        self.assertIn(
            "system.storage.predictive_optimization_operations_history",
            templates,
        )
        self.assertIn("CLUSTER BY AUTO", auditor)
        self.assertIn("apply_approved", auditor)
        self.assertIn("approved_tables", auditor)
        self.assertIn("`auto_apply_high_confidence` is not a", auditor)
        self.assertIn("Data-layout DDL is never automatic", orchestrator)
        self.assertIn("Never run `OPTIMIZE`", auditor)
        self.assertIn("applied-actions-ledger.md", auditor)

    def test_applied_actions_are_written_to_a_ledger(self) -> None:
        ledger = (SKILLS / "applied-actions-ledger.md").read_text(encoding="utf-8")
        publisher = read_skill("catalog-metadata-publisher")
        builder = read_skill("semantic-view-builder")
        orchestrator = read_skill("semantic-onboarding")
        self.assertIn("applied_actions.sql", ledger)
        self.assertIn("applied_actions.py", ledger)
        self.assertIn("Dry runs do not write a ledger", ledger)
        self.assertIn("applied-actions-ledger.md", publisher)
        self.assertIn("applied-actions-ledger.md", builder)
        self.assertIn("applied-actions-ledger.md", orchestrator)
        self.assertIn("mutating API request", ledger)
        self.assertIn("before/after JSON", ledger)

    def test_benchmark_builder_requires_scope_and_review(self) -> None:
        skill = read_skill("genie-benchmark-builder")
        contract = read_skill("genie-benchmark-builder", "benchmark-contract.md")
        self.assertIn("Default to `dry_run`", skill)
        self.assertIn("Reject unbounded metastore discovery", skill)
        self.assertIn("maximum 500 benchmark questions", skill)
        for status in (
            "`in_scope`",
            "`partially_answerable`",
            "`ambiguous`",
            "`out_of_scope`",
        ):
            self.assertIn(status, skill)
        self.assertIn("review_status: approved", skill)
        self.assertIn("32-character hexadecimal", contract)
        self.assertIn("Never persist raw result rows", contract)

    def test_benchmark_publication_preserves_agent_configuration(self) -> None:
        skill = read_skill("genie-benchmark-builder")
        api = read_skill("genie-benchmark-builder", "api-templates.md")
        orchestrator = read_skill("semantic-onboarding")
        self.assertIn("apply_approved", skill)
        self.assertIn("approved_question_ids", skill)
        self.assertIn("preserve every unrelated serialized field", skill)
        self.assertIn("genie_space.before.json", skill)
        self.assertIn("rollback payload", skill)
        self.assertIn("Never send a partial", api)
        self.assertIn("If-Match", api)
        self.assertIn("already_applied", api)
        self.assertIn("Benchmark publication is never automatic", orchestrator)

    def test_benchmark_ground_truth_is_validated_before_publish(self) -> None:
        skill = read_skill("genie-benchmark-builder")
        review = read_skill("genie-benchmark-builder", "benchmark-review.sql")
        self.assertIn("Allow one read-only `SELECT` or `WITH`", skill)
        self.assertIn("Parse or explain the SQL", skill)
        self.assertIn("result signature", skill)
        self.assertIn("A reviewer must set", skill)
        self.assertIn("review_status: pending", review)
        self.assertIn("do not publish", review.lower())

    def test_repeated_runs_are_idempotent(self) -> None:
        contract = read_skill("semantic-onboarding", "run-contract.md")
        self.assertIn("Treat an exact existing state as `already_applied`", contract)
        self.assertIn("definition hash", contract)

    def test_metric_template_has_required_structure(self) -> None:
        template = read_skill("semantic-view-builder", "metric-view-template.md")
        required = [
            "WITH METRICS",
            "LANGUAGE YAML",
            "version: 1.1",
            "source:",
            "fields:",
            "measures:",
            "at_most_one_match: true",
        ]
        for token in required:
            self.assertIn(token, template)

    def test_sparse_extraction_requires_ocr(self) -> None:
        script = (
            SKILLS
            / "document-schema-extractor"
            / "scripts"
            / "extract_pdf.py"
        )
        spec = importlib.util.spec_from_file_location("extract_pdf", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            result = module.build_result(Path(handle.name), "test", ["", "image"], 20)
        self.assertEqual("OCR_REQUIRED", result["status"])
        self.assertEqual(2, result["page_count"])


if __name__ == "__main__":
    unittest.main()
