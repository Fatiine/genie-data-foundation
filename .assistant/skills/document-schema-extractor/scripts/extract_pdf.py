#!/usr/bin/env python3
"""Extract page-level PDF text without changing the source document.

Uses pypdf when available and falls back to the `pdftotext` executable.
This is a text extraction fallback, not OCR.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def extract_with_pypdf(path: Path) -> tuple[str, list[str]]:
    from pypdf import PdfReader  # type: ignore[import-not-found]

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise RuntimeError("PDF is encrypted and cannot be read") from exc
    return "pypdf", [(page.extract_text() or "") for page in reader.pages]


def extract_with_pdftotext(path: Path) -> tuple[str, list[str]]:
    executable = shutil.which("pdftotext")
    if not executable:
        raise RuntimeError("Neither pypdf nor the pdftotext executable is available")
    result = subprocess.run(
        [executable, "-layout", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        message = result.stderr.strip() or "unknown pdftotext error"
        raise RuntimeError(f"pdftotext failed: {message}")
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return "pdftotext", pages


def extract(path: Path) -> tuple[str, list[str]]:
    try:
        return extract_with_pypdf(path)
    except ImportError:
        return extract_with_pdftotext(path)


def build_result(path: Path, method: str, pages: list[str], min_chars: int) -> dict[str, Any]:
    page_records = []
    sparse_pages = 0
    for number, raw_text in enumerate(pages, start=1):
        text = raw_text.strip()
        char_count = len(text)
        if char_count < min_chars:
            sparse_pages += 1
        page_records.append(
            {
                "page_number": number,
                "char_count": char_count,
                "text": text,
            }
        )

    total_chars = sum(page["char_count"] for page in page_records)
    sparse_ratio = sparse_pages / len(page_records) if page_records else 1.0
    needs_ocr = not page_records or total_chars < min_chars or sparse_ratio > 0.8
    return {
        "document_path": str(path),
        "document_id": file_hash(path),
        "extraction_method": method,
        "status": "OCR_REQUIRED" if needs_ocr else "OK",
        "page_count": len(page_records),
        "total_chars": total_chars,
        "sparse_page_count": sparse_pages,
        "pages": page_records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract page-level text from a PDF")
    parser.add_argument("pdf", type=Path, help="Path to a PDF")
    parser.add_argument(
        "--format",
        choices=("json", "jsonl"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        default=20,
        help="Threshold used to detect image-only/sparse pages",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 2 when OCR is required",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.pdf.expanduser().resolve()
    if not path.is_file():
        print(json.dumps({"status": "ERROR", "error": f"File not found: {path}"}))
        return 1
    if path.suffix.lower() != ".pdf":
        print(json.dumps({"status": "ERROR", "error": "Input must be a PDF"}))
        return 1
    if args.min_chars_per_page < 0:
        print(json.dumps({"status": "ERROR", "error": "Threshold must be non-negative"}))
        return 1

    try:
        method, pages = extract(path)
        result = build_result(path, method, pages, args.min_chars_per_page)
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc), "document_path": str(path)}))
        return 1

    if args.format == "json":
        json.dump(result, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        metadata = {key: value for key, value in result.items() if key != "pages"}
        print(json.dumps({"record_type": "document", **metadata}, ensure_ascii=False))
        for page in result["pages"]:
            print(json.dumps({"record_type": "page", **page}, ensure_ascii=False))

    return 2 if args.strict and result["status"] == "OCR_REQUIRED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
