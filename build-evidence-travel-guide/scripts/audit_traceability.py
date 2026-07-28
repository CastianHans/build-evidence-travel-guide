#!/usr/bin/env python3
"""Audit user requirements and candidate-to-PDF traceability."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_FIELDS = {
    "requirement_id",
    "source",
    "requirement",
    "required",
    "candidate_ids",
    "pdf_section",
    "status",
    "verification",
    "notes",
}
SOURCE = {"user_confirmed", "supplied_file", "official", "planner", "acceptance"}
STATUS = {"satisfied", "declared_gap", "not_applicable", "pending"}


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def norm(value: str) -> str:
    return (value or "").strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--mode", choices=["provisional", "final"], default="final")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()
    trace_path = root / "requirements" / "traceability.csv"
    candidate_path = root / "research" / "candidates.csv"
    if not trace_path.exists() or not candidate_path.exists():
        raise SystemExit("Missing requirements/traceability.csv or research/candidates.csv")
    fields, rows = load_csv(trace_path)
    _, candidates = load_csv(candidate_path)
    errors = [
        f"traceability.csv: missing v1.2 column {field_name}"
        for field_name in sorted(REQUIRED_FIELDS - set(fields))
    ]
    candidate_map = {
        (row.get("candidate_id") or "").strip(): row
        for row in candidates
        if (row.get("candidate_id") or "").strip()
    }
    requirement_ids: set[str] = set()
    mapped_candidates: set[str] = set()
    pending_required: list[str] = []
    declared_gaps: list[str] = []

    for row_number, row in enumerate(rows, start=2):
        prefix = f"traceability.csv:{row_number}"
        requirement_id = (row.get("requirement_id") or "").strip()
        if not requirement_id:
            errors.append(f"{prefix}: requirement_id is required")
            continue
        if requirement_id in requirement_ids:
            errors.append(f"{prefix}: duplicate requirement_id {requirement_id}")
            continue
        requirement_ids.add(requirement_id)
        source = norm(row.get("source"))
        required = norm(row.get("required"))
        status = norm(row.get("status"))
        if source not in SOURCE:
            errors.append(f"{prefix}: invalid source {source}")
        if required not in {"yes", "no"}:
            errors.append(f"{prefix}: required must be yes or no")
        if status not in STATUS:
            errors.append(f"{prefix}: invalid status {status}")
        if not (row.get("requirement") or "").strip():
            errors.append(f"{prefix}: requirement is required")
        candidate_ids = [
            value.strip()
            for value in (row.get("candidate_ids") or "").split(";")
            if value.strip()
        ]
        for candidate_id in candidate_ids:
            if candidate_id not in candidate_map:
                errors.append(f"{prefix}: unknown candidate_id {candidate_id}")
            else:
                mapped_candidates.add(candidate_id)
        if status == "satisfied":
            if not (row.get("pdf_section") or "").strip():
                errors.append(f"{prefix}: satisfied requirement requires pdf_section")
            if not (row.get("verification") or "").strip():
                errors.append(f"{prefix}: satisfied requirement requires verification")
        if required == "yes" and status != "satisfied":
            pending_required.append(requirement_id)
        if status == "declared_gap":
            declared_gaps.append(requirement_id)
            if not (row.get("notes") or "").strip():
                errors.append(f"{prefix}: declared_gap requires notes")

    for candidate_id, candidate in candidate_map.items():
        if norm(candidate.get("status")) not in {"included", "optional"}:
            continue
        if norm(candidate.get("importance")) not in {"critical", "major"}:
            continue
        if candidate_id not in mapped_candidates:
            errors.append(
                f"candidate {candidate_id}: included/optional critical or major candidate "
                "is not mapped to any requirement/PDF section"
            )

    failures = list(pending_required) if args.mode == "final" else []
    lines = [
        "# Requirements traceability audit",
        "",
        f"- Mode: {args.mode}",
        f"- Requirements: {len(rows)}",
        f"- Required but unsatisfied: {len(pending_required)}",
        f"- Declared gaps: {len(declared_gaps)}",
        f"- Mapped candidates: {len(mapped_candidates)}",
        f"- Validation errors: {len(errors)}",
    ]
    if pending_required:
        lines.extend(["", "## Required but unsatisfied", ""])
        lines.extend(f"- {item}" for item in pending_required)
    if declared_gaps:
        lines.extend(["", "## Declared gaps", ""])
        lines.extend(f"- {item}" for item in declared_gaps)
    if errors:
        lines.extend(["", "## Validation errors", ""])
        lines.extend(f"- {item}" for item in errors)
    output = args.output or root / "requirements" / "traceability-audit.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 3
    if failures:
        print(f"FAIL: {len(failures)} required requirements are not satisfied.")
        return 2
    print("PASS: requirements are traceable for the selected mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
