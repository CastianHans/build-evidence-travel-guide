#!/usr/bin/env python3
"""Run the completion state machine; only a full green run may become FINAL."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run_check(name: str, command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    print(f"\n===== {name} (exit {completed.returncode}) =====")
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip())
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def audit_visual_manifest(path: Path, expected_pages: int) -> list[str]:
    if not path.exists():
        return [f"visual inspection manifest not found: {path}"]
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors: list[str] = []
    if len(rows) != expected_pages:
        errors.append(
            f"visual manifest page count mismatch: expected {expected_pages}, got {len(rows)}"
        )
    seen: set[int] = set()
    for row_number, row in enumerate(rows, start=2):
        try:
            page = int((row.get("page") or "").strip())
        except ValueError:
            errors.append(f"visual manifest row {row_number}: invalid page")
            continue
        if page in seen:
            errors.append(f"visual manifest row {row_number}: duplicate page {page}")
        seen.add(page)
        if (row.get("status") or "").strip().lower() != "pass":
            errors.append(f"visual manifest page {page}: status is not pass")
        if not (row.get("inspector") or "").strip():
            errors.append(f"visual manifest page {page}: inspector is required")
        try:
            datetime.fromisoformat((row.get("inspected_at") or "").strip())
        except ValueError:
            errors.append(f"visual manifest page {page}: inspected_at must be ISO format")
        image = Path((row.get("image") or "").strip())
        if not image.is_absolute():
            image = path.parent / image
        if not image.exists():
            errors.append(f"visual manifest page {page}: rendered image not found")
    if seen and seen != set(range(1, expected_pages + 1)):
        errors.append("visual manifest page numbers are not complete and contiguous")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--mode", choices=["provisional", "final"], default="final")
    parser.add_argument("--document-version", required=True)
    parser.add_argument("--visual-manifest", type=Path)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--forbid", action="append", default=[])
    parser.add_argument("--forecast-issued")
    parser.add_argument("--trip-start")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.project_dir.expanduser().resolve()
    pdf = args.pdf.expanduser().resolve()
    scripts = Path(__file__).resolve().parent
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}")

    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise SystemExit("Install pypdf: python -m pip install pypdf") from error
    reader = PdfReader(str(pdf))
    page_count = len(reader.pages)
    opening_text = "\n".join(
        (page.extract_text() or "") for page in reader.pages[: min(3, page_count)]
    )
    opening_errors = []
    if not any(term in opening_text for term in {"天气", "Weather", "weather"}):
        opening_errors.append("weather section is not in the first three pages")
    if not any(
        term in opening_text
        for term in {
            "出发前准备",
            "旅行前准备",
            "行前准备",
            "Pre-departure preparation",
            "Predeparture preparation",
        }
    ):
        opening_errors.append("pre-departure preparation is not in the first three pages")

    checks = [
        run_check(
            "traceability",
            [
                sys.executable,
                str(scripts / "audit_traceability.py"),
                str(root),
                "--mode",
                args.mode,
            ],
        ),
        run_check(
            "evidence",
            [sys.executable, str(scripts / "audit_evidence.py"), str(root)],
        ),
        run_check(
            "reputation",
            [sys.executable, str(scripts / "audit_reputation.py"), str(root)],
        ),
        run_check(
            "itinerary",
            [sys.executable, str(scripts / "audit_itinerary.py"), str(root)],
        ),
    ]

    evidence_count = row_count(root / "research" / "evidence.csv")
    candidate_count = row_count(root / "research" / "candidates.csv")
    pdf_json = root / "work" / "pdf-validation.json"
    validate_command = [
        sys.executable,
        str(scripts / "validate_pdf.py"),
        str(pdf),
        "--document-version",
        args.document_version,
        "--require-version-in-filename",
        "--require-metadata-title",
        "--require-regex",
        r"(天气|[Ww]eather)",
        "--require-regex",
        rf"(证据台账[^0-9]{{0,12}}{evidence_count}\s*条|"
        rf"[Ee]vidence ledger[^0-9]{{0,12}}{evidence_count}\s*rows?)",
        "--require-regex",
        rf"(候选对象[^0-9]{{0,12}}{candidate_count}\s*项|"
        rf"[Cc]andidates?[^0-9]{{0,12}}{candidate_count}\s*items?)",
        "--output-json",
        str(pdf_json),
    ]
    for term in args.require:
        validate_command.extend(["--require", term])
    for term in args.forbid:
        validate_command.extend(["--forbid", term])
    if args.forecast_issued or args.trip_start:
        if not (args.forecast_issued and args.trip_start):
            raise SystemExit("--forecast-issued and --trip-start must be supplied together")
        validate_command.extend(
            [
                "--forecast-issued",
                args.forecast_issued,
                "--trip-start",
                args.trip_start,
            ]
        )
    checks.append(run_check("pdf", validate_command))

    visual_manifest = (
        args.visual_manifest.expanduser().resolve()
        if args.visual_manifest
        else root / "work" / "visual-inspection.csv"
    )
    visual_errors = audit_visual_manifest(visual_manifest, page_count)
    if visual_errors:
        print("\n===== visual inspection =====")
        for error in visual_errors:
            print(f"ERROR: {error}")
    if opening_errors:
        print("\n===== opening sections =====")
        for error in opening_errors:
            print(f"ERROR: {error}")

    failed_checks = [item["name"] for item in checks if item["returncode"] != 0]
    all_failures = failed_checks + opening_errors + visual_errors
    final_allowed = args.mode == "final" and not all_failures
    status = "final" if final_allowed else "provisional"
    timestamp = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": "1.2",
        "requested_mode": args.mode,
        "status": status,
        "final_allowed": final_allowed,
        "verified_at": timestamp,
        "document_version": args.document_version,
        "pdf": str(pdf),
        "pdf_pages": page_count,
        "pdf_bytes": pdf.stat().st_size,
        "pdf_sha256": sha256(pdf),
        "candidate_rows": candidate_count,
        "evidence_rows": evidence_count,
        "checks": checks,
        "opening_errors": opening_errors,
        "visual_manifest": str(visual_manifest),
        "visual_errors": visual_errors,
        "failures": all_failures,
    }
    output = (
        args.output.expanduser().resolve()
        if args.output
        else root / "work" / "finalization-manifest.json"
    )
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    state = root / "work" / "run-state.json"
    state.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "status": status,
                "verified_at": timestamp,
                "manifest": str(output),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nmanifest={output}")
    print(f"status={status}")
    if final_allowed:
        print("FINAL: every required completion gate passed.")
        return 0
    if args.mode == "provisional":
        print("PROVISIONAL: gaps are recorded; do not describe this artifact as final.")
        return 0
    print("BLOCKED: final status is forbidden until every gate passes.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
