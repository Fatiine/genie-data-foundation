# Contributing

Contributions that improve document extraction, Unity Catalog safety, semantic modeling, or customer usability are welcome.

## Rules

- Use synthetic schemas and examples.
- Never commit customer data, vendor documentation, credentials, extracted document text, or generated reports.
- Keep each `SKILL.md` focused and below 500 lines.
- Preserve evidence citations and fail-closed behavior.
- Do not weaken dry-run defaults or automatic-publication thresholds without explaining the safety impact.
- Treat Databricks PK/FK constraints as informational.

## Validate changes

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .assistant/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 .assistant/tests/validate_skills.py
```

For changes to document extraction, test both:

- a text-based synthetic PDF
- an image-only or sparse document that must return `OCR_REQUIRED`

For changes to metadata publication or semantic views, include dry-run coverage for conflicting metadata, invalid keys, join fanout, and repeated execution.
