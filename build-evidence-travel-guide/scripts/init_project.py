#!/usr/bin/env python3
"""Create the ledgers required by the evidence-travel workflow."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


CANDIDATE_FIELDS = [
    "candidate_id",
    "name",
    "local_name",
    "category",
    "branch_or_variant",
    "importance",
    "route_role",
    "planned_date",
    "status",
    "positive_target",
    "negative_target",
    "official_target",
    "operational_target",
    "source_family_target",
    "reputation_required",
    "rejection_reason",
    "replacement_candidate_id",
    "notes",
]

EVIDENCE_FIELDS = [
    "evidence_id",
    "candidate_id",
    "platform",
    "source_family",
    "source_type",
    "polarity",
    "relevance",
    "access_level",
    "experience_type",
    "promotion",
    "commercial_signal",
    "attack_signal",
    "identity_check",
    "branch_or_variant",
    "independence_cluster_id",
    "incident_specificity",
    "artifact_support",
    "discrimination_class",
    "matched_comparison",
    "target_group",
    "published_at",
    "retrieved_at",
    "freshness_status",
    "title",
    "author",
    "claim",
    "excerpt",
    "decision_effect",
    "business_response",
    "url",
    "content_fingerprint",
    "reviewer",
    "notes",
]

COMMENT_FIELDS = [
    "comment_id",
    "parent_evidence_id",
    "candidate_id",
    "platform",
    "source_family",
    "stance",
    "experience_type",
    "access_level",
    "identity_check",
    "same_incident",
    "new_fact",
    "independence_cluster_id",
    "commercial_signal",
    "attack_signal",
    "incident_specificity",
    "artifact_support",
    "discrimination_class",
    "matched_comparison",
    "target_group",
    "published_at",
    "retrieved_at",
    "author",
    "excerpt",
    "permalink",
    "reviewer",
    "notes",
]

TRACEABILITY_FIELDS = [
    "requirement_id",
    "source",
    "requirement",
    "required",
    "candidate_ids",
    "pdf_section",
    "status",
    "verification",
    "notes",
]

ITINERARY_FIELDS = [
    "day_id",
    "sequence",
    "candidate_id",
    "stop_name",
    "start_time",
    "end_time",
    "transit_minutes",
    "search_buffer_minutes",
    "activity_minutes",
    "meal_rest_minutes",
    "contingency_minutes",
    "mode",
    "route_detail",
    "hotel_start",
    "hotel_return",
    "fallback_day_id",
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

COMMENT_LIMITATIONS_TEMPLATE = """# Comment evidence limitations

- Platforms/comments inspected:
- Sort order or sampling method:
- Whether replies were expanded:
- Known moderation, deletion, login, rate-limit, or visibility limits:
- How same-incident, copied, bare-agreement, merchant, and suspected coordinated comments were handled:
- Reviewer and review time:
"""


def ensure_csv(path: Path, fields: list[str]) -> None:
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            existing_fields = list(reader.fieldnames or [])
            rows = list(reader)
        missing = [field for field in fields if field not in existing_fields]
        if not missing:
            return
        upgraded_fields = existing_fields + missing
        temporary = path.with_suffix(path.suffix + ".upgrade")
        with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=upgraded_fields)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
        print(f"Upgraded {path.name} with columns: {', '.join(missing)}")
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

    limitations = root / "research" / "comment-limitations.md"
    if not limitations.exists():
        limitations.write_text(COMMENT_LIMITATIONS_TEMPLATE, encoding="utf-8")

    ensure_csv(root / "requirements" / "traceability.csv", TRACEABILITY_FIELDS)
    ensure_csv(root / "research" / "candidates.csv", CANDIDATE_FIELDS)
    ensure_csv(root / "research" / "evidence.csv", EVIDENCE_FIELDS)
    ensure_csv(root / "research" / "comments.csv", COMMENT_FIELDS)
    ensure_csv(root / "work" / "itinerary.csv", ITINERARY_FIELDS)

    state = root / "work" / "run-state.json"
    if not state.exists():
        state.write_text(
            json.dumps(
                {
                    "schema_version": "1.2",
                    "status": "initialized",
                    "allowed_statuses": [
                        "initialized",
                        "researching",
                        "planning",
                        "provisional",
                        "final",
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(root)
    print("Created v1.2 ledgers without overwriting existing files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
