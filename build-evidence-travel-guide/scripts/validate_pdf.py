#!/usr/bin/env python3
"""Perform text, metadata, version, weather-window, and checksum checks on a PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--require-regex", action="append", default=[])
    parser.add_argument("--forbid", action="append", default=[])
    parser.add_argument("--document-version")
    parser.add_argument("--require-version-in-filename", action="store_true")
    parser.add_argument("--metadata-title")
    parser.add_argument("--require-metadata-title", action="store_true")
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--min-text", type=int, default=20)
    parser.add_argument("--forecast-issued")
    parser.add_argument("--trip-start")
    parser.add_argument("--forecast-window-days", type=int, default=14)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise SystemExit("Install pypdf: python -m pip install pypdf") from error

    path = args.pdf.expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"PDF not found: {path}")
    reader = PdfReader(str(path))
    page_text = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page_text)
    low_text = [
        index + 1 for index, value in enumerate(page_text) if len(value) < args.min_text
    ]
    missing = [term for term in args.require if term not in text]
    missing_regex = [
        pattern
        for pattern in args.require_regex
        if re.search(pattern, text, flags=re.MULTILINE) is None
    ]
    forbidden = [term for term in args.forbid if term and term in text]
    errors: list[str] = []
    if low_text:
        errors.append(f"low-text pages: {low_text}")
    if missing:
        errors.append(f"missing required terms: {missing}")
    if missing_regex:
        errors.append(f"missing required regex patterns: {missing_regex}")
    if forbidden:
        errors.append(f"forbidden stale terms present: {forbidden}")
    if args.expected_pages is not None and len(reader.pages) != args.expected_pages:
        errors.append(
            f"page count mismatch: expected {args.expected_pages}, got {len(reader.pages)}"
        )
    if args.document_version:
        if args.document_version not in text:
            errors.append(f"document version {args.document_version!r} not found in PDF text")
        if args.require_version_in_filename and args.document_version not in path.stem:
            errors.append(
                f"document version {args.document_version!r} not found in filename"
            )
    metadata = reader.metadata or {}
    title = str(metadata.get("/Title") or "")
    if args.metadata_title and title != args.metadata_title:
        errors.append(f"metadata title mismatch: expected {args.metadata_title!r}, got {title!r}")
    if args.require_metadata_title and not title.strip():
        errors.append("metadata title is required")
    if bool(args.forecast_issued) != bool(args.trip_start):
        errors.append("--forecast-issued and --trip-start must be supplied together")
    elif args.forecast_issued and args.trip_start:
        issued = date.fromisoformat(args.forecast_issued)
        trip_start = date.fromisoformat(args.trip_start)
        horizon = (trip_start - issued).days
        if horizon > args.forecast_window_days and "远期趋势，非逐日预报" not in text:
            errors.append(
                "trip is outside the forecast window; PDF must say "
                "'远期趋势，非逐日预报'"
            )

    result = {
        "path": str(path),
        "pages": len(reader.pages),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "text_characters": len(text),
        "metadata_title": title,
        "low_text_pages": low_text,
        "missing_required_terms": missing,
        "missing_required_regex": missing_regex,
        "forbidden_terms_present": forbidden,
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    for key, value in result.items():
        print(f"{key}={value}")
    if args.output_json:
        output = args.output_json.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
