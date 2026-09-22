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
