#!/usr/bin/env python3
"""Create a safe, reusable workspace for an evidence-backed travel guide."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


CANDIDATE_FIELDS = [
    "candidate_id",
    "name",
    "local_name",
    "category",
    "importance",
    "route_role",
    "planned_date",
    "status",
    "positive_target",
    "negative_target",
    "official_target",
    "operational_target",
    "platform_target",
    "notes",
]

EVIDENCE_FIELDS = [
    "evidence_id",
    "candidate_id",
    "platform",
    "source_type",
    "polarity",
    "relevance",
    "experience_type",
    "promotion",
    "identity_check",
    "published_at",
    "retrieved_at",
    "title",
    "author",
    "claim",
    "excerpt",
    "decision_effect",
    "url",
    "content_fingerprint",
    "reviewer",
    "notes",
]

REQUIREMENTS_TEMPLATE = """# Travel requirements ledger

## User-confirmed facts

## User preferences

## Supplied-source facts

## Unknowns and conflicts

## Assumptions requiring confirmation

## Output and acceptance requirements

## Safety, privacy, and authorization boundaries
"""


def create_csv(path: Path, fields: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fields).writeheader()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()

    for relative in [
        "requirements",
        "research/raw",
        "research/notes",
        "research/analysis",
        "work",
        "outputs",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    requirements = root / "requirements" / "requirements.md"
    if not requirements.exists():
        requirements.write_text(REQUIREMENTS_TEMPLATE, encoding="utf-8")

    create_csv(root / "research" / "candidates.csv", CANDIDATE_FIELDS)
    create_csv(root / "research" / "evidence.csv", EVIDENCE_FIELDS)

    print(root)
    print("Created reusable ledgers without overwriting existing files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
