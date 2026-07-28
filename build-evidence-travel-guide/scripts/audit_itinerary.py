#!/usr/bin/env python3
"""Audit hotel-anchored day arithmetic and candidate traceability."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


REQUIRED_FIELDS = {
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
}


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def minutes(value: str) -> int:
    parsed = datetime.strptime(value.strip(), "%H:%M")
    return parsed.hour * 60 + parsed.minute


def nonnegative_integer(value: str, field_name: str) -> int:
    result = int((value or "").strip())
    if result < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tolerance", type=int, default=5)
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()
    itinerary_path = root / "work" / "itinerary.csv"
    candidate_path = root / "research" / "candidates.csv"
    if not itinerary_path.exists() or not candidate_path.exists():
        raise SystemExit("Missing work/itinerary.csv or research/candidates.csv")

    fields, rows = load_csv(itinerary_path)
    _, candidates = load_csv(candidate_path)
    candidate_map = {
        (row.get("candidate_id") or "").strip(): row
        for row in candidates
        if (row.get("candidate_id") or "").strip()
    }
    errors = [
        f"itinerary.csv: missing v1.2 column {field_name}"
        for field_name in sorted(REQUIRED_FIELDS - set(fields))
    ]
    days: dict[str, list[dict[str, object]]] = defaultdict(list)

    for row_number, row in enumerate(rows, start=2):
        prefix = f"itinerary.csv:{row_number}"
        try:
            day_id = (row.get("day_id") or "").strip()
            candidate_id = (row.get("candidate_id") or "").strip()
            stop_name = (row.get("stop_name") or "").strip()
            if not day_id or not stop_name:
                raise ValueError("day_id and stop_name are required")
            if candidate_id not in candidate_map:
                raise ValueError(f"unknown candidate_id {candidate_id}")
            sequence = int((row.get("sequence") or "").strip())
            if sequence < 1:
                raise ValueError("sequence must be at least 1")
            start = minutes(row.get("start_time") or "")
            end = minutes(row.get("end_time") or "")
            if end <= start:
                raise ValueError("end_time must be after start_time within the same day")
            components = {
                field_name: nonnegative_integer(row.get(field_name) or "", field_name)
                for field_name in [
                    "transit_minutes",
                    "search_buffer_minutes",
                    "activity_minutes",
                    "meal_rest_minutes",
                    "contingency_minutes",
                ]
            }
            component_total = sum(components.values())
            elapsed = end - start
            if abs(elapsed - component_total) > args.tolerance:
                raise ValueError(
                    f"time arithmetic mismatch: elapsed {elapsed}, components {component_total}"
                )
            if not (row.get("mode") or "").strip():
                raise ValueError("mode is required")
            if not (row.get("route_detail") or "").strip():
                raise ValueError("route_detail is required")
            hotel_start = (row.get("hotel_start") or "").strip().lower()
            hotel_return = (row.get("hotel_return") or "").strip().lower()
            if hotel_start not in {"yes", "no"} or hotel_return not in {"yes", "no"}:
                raise ValueError("hotel_start and hotel_return must be yes or no")
        except (ValueError, TypeError) as error:
            errors.append(f"{prefix}: {error}")
            continue
        days[day_id].append(
            {
                "sequence": sequence,
                "start": start,
                "end": end,
                "candidate_id": candidate_id,
                "stop_name": stop_name,
                "hotel_start": hotel_start,
                "hotel_return": hotel_return,
                "fallback_day_id": (row.get("fallback_day_id") or "").strip(),
                "elapsed": elapsed,
                "transit": components["transit_minutes"],
                "activity": components["activity_minutes"],
                "meal_rest": components["meal_rest_minutes"],
                "buffer": components["search_buffer_minutes"]
                + components["contingency_minutes"],
            }
        )

    lines = [
        "# Itinerary feasibility audit",
        "",
        "| Day | Rows | Elapsed | Transit | Activity | Meal/rest | Buffer | Result |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    day_failures = 0
    for day_id in sorted(days):
        day = sorted(days[day_id], key=lambda item: int(item["sequence"]))
        problems: list[str] = []
        sequences = [int(item["sequence"]) for item in day]
        if sequences != list(range(1, len(day) + 1)):
            problems.append("sequence is not contiguous from 1")
        if len(day) < 3:
            problems.append("day needs hotel departure, at least one stop, and hotel return")
        if day and day[0]["hotel_start"] != "yes":
            problems.append("first row is not anchored at the hotel")
        if day and day[-1]["hotel_return"] != "yes":
            problems.append("last row does not return to the hotel")
        if day:
            first_candidate = str(day[0]["candidate_id"])
            last_candidate = str(day[-1]["candidate_id"])
            if first_candidate != last_candidate:
                problems.append("day does not return to the same hotel candidate")
            hotel_category = (
                candidate_map[first_candidate].get("category") or ""
            ).strip().lower()
            if hotel_category not in {"hotel", "lodging", "accommodation"}:
                problems.append(
                    "hotel_start candidate category must be hotel/lodging/accommodation"
                )
        if sum(item["hotel_start"] == "yes" for item in day) != 1:
            problems.append("hotel_start=yes must appear exactly once")
        if sum(item["hotel_return"] == "yes" for item in day) != 1:
            problems.append("hotel_return=yes must appear exactly once")
        if not any(item["fallback_day_id"] for item in day):
            problems.append("day has no complete fallback_day_id")
        for previous, current in zip(day, day[1:]):
            if int(current["start"]) < int(previous["end"]):
                problems.append(
                    f"overlap between sequence {previous['sequence']} and {current['sequence']}"
                )
            elif int(current["start"]) - int(previous["end"]) > args.tolerance:
                problems.append(
                    f"unallocated time gap between sequence {previous['sequence']} "
                    f"and {current['sequence']}"
                )
        if problems:
            day_failures += 1
        totals = {
            key: sum(int(item[key]) for item in day)
            for key in ["elapsed", "transit", "activity", "meal_rest", "buffer"]
        }
        result = "PASS" if not problems else "FAIL: " + "; ".join(problems)
        lines.append(
            f"| {day_id.replace('|', '/')} | {len(day)} | {totals['elapsed']} | "
            f"{totals['transit']} | {totals['activity']} | {totals['meal_rest']} | "
            f"{totals['buffer']} | {result} |"
        )

    if not days:
        errors.append("itinerary.csv contains no valid rows")
    lines.extend(
        [
            "",
            f"- Days audited: {len(days)}",
            f"- Day failures: {day_failures}",
            f"- Validation errors: {len(errors)}",
        ]
    )
    if errors:
        lines.extend(["", "## Validation errors", ""])
        lines.extend(f"- {item}" for item in errors)

    output = args.output or root / "work" / "itinerary-audit.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 3
    if day_failures:
        print(f"FAIL: {day_failures} day plans are not executable.")
        return 2
    print("PASS: all day plans are hotel-anchored and arithmetically feasible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
