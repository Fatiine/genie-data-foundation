#!/usr/bin/env python3
"""Static checks for the project-staged Genie Code skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED = {
    "semantic-onboarding",
    "document-schema-extractor",
    "catalog-semantic-profiler",
    "catalog-metadata-publisher",
    "semantic-view-builder",
}
NAME_PATTERN = re.compile(r"^[a-z0-9-]{1,64}$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        metadata = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{path}: {exc}"]

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if name != path.parent.name:
        errors.append(f"{path}: name must match directory")
    if not NAME_PATTERN.fullmatch(name):
        errors.append(f"{path}: invalid name")
    if not description or len(description) > 1024:
        errors.append(f"{path}: invalid description")
    if "Use " not in description and "use " not in description:
        errors.append(f"{path}: description should state when to use the skill")
    if len(text.splitlines()) > 500:
        errors.append(f"{path}: exceeds 500 lines")

    for link in LINK_PATTERN.findall(text):
        if "://" in link or link.startswith("#"):
            continue
        target = (path.parent / link).resolve()
        if not target.exists():
            errors.append(f"{path}: broken link {link}")
    return errors


def main() -> int:
    found = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
    errors = [f"missing skill: {name}" for name in sorted(EXPECTED - found)]
    errors.extend(f"unexpected skill: {name}" for name in sorted(found - EXPECTED))
    for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
        errors.extend(validate_skill(skill_file))

    extractor = SKILLS / "document-schema-extractor" / "scripts" / "extract_pdf.py"
    if not extractor.exists():
        errors.append("missing PDF extraction fallback")
    else:
        try:
            compile(extractor.read_text(encoding="utf-8"), str(extractor), "exec")
        except SyntaxError as exc:
            errors.append(f"{extractor}: {exc}")

    metric_template = (
        SKILLS / "semantic-view-builder" / "metric-view-template.md"
    ).read_text(encoding="utf-8")
    for token in ("WITH METRICS", "LANGUAGE YAML", "version: 1.1", "measures:"):
        if token not in metric_template:
            errors.append(f"metric template missing {token}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"OK: validated {len(found)} Genie Code skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
