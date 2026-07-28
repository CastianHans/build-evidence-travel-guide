#!/usr/bin/env python3
"""Perform text, blank-page, metadata, and checksum checks on a PDF."""

from __future__ import annotations

import argparse
import hashlib
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
    parser.add_argument("--min-text", type=int, default=20)
    args = parser.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise SystemExit("Install pypdf: python -m pip install pypdf") from error

    path = args.pdf.expanduser().resolve()
    reader = PdfReader(str(path))
    page_text = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page_text)
    blank = [index + 1 for index, value in enumerate(page_text) if len(value) < args.min_text]
    missing = [term for term in args.require if term not in text]

    print(f"path={path}")
    print(f"pages={len(reader.pages)}")
    print(f"bytes={path.stat().st_size}")
    print(f"sha256={sha256(path)}")
    print(f"text_characters={len(text)}")
    print(f"low_text_pages={blank}")
    print(f"missing_required_terms={missing}")

    return 2 if blank or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
