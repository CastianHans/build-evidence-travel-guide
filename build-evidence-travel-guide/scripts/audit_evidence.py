#!/usr/bin/env python3
"""Strictly audit unique candidate-level travel evidence."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


DEFAULTS = {
    "critical": (2, 2, 1, 1, 2),
    "major": (2, 2, 1, 0, 1),
    "minor": (1, 1, 0, 0, 1),
}
IMPORTANCE = set(DEFAULTS)
STATUS = {"candidate", "included", "optional", "rejected"}
SOURCE_TYPE = {
    "social",
    "official",
    "operational_failure",
    "map_review",
    "blog",
    "news",
}
POLARITY = {"positive", "negative", "mixed", "neutral", "official"}
RELEVANCE = {"direct", "partial", "mismatch"}
EXPERIENCE_TYPE = {
    "first_hand",
    "comment",
    "indexed_excerpt",
    "official",
    "second_hand",
}
PROMOTION = {"no", "possible", "yes"}
IDENTITY_CHECK = {"yes", "no", "unknown"}
TRACKING_KEYS = {
    "xsec_token",
    "xsec_source",
    "source",
    "share_id",
    "shareid",
    "app_platform",
    "app_version",
}


def normalized(value: str) -> str:
    return (value or "").strip().lower()


def md_cell(value: str) -> str:
    return (value or "").replace("|", r"\|").replace("\r", " ").replace("\n", " ").strip()


def integer(value: str, fallback: int) -> int:
    value = (value or "").strip()
    result = int(value) if value else fallback
    if result < 0:
        raise ValueError("targets cannot be negative")
    return result


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def canonical_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be absolute HTTP(S)")
    query = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_KEYS:
            continue
        query.append((key, item))
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            urlencode(sorted(query)),
            "",
        )
    )


def valid_date(value: str, field: str, allow_blank: bool = False) -> str | None:
    value = (value or "").strip()
    if not value and allow_blank:
        return None
    if not value:
        raise ValueError(f"{field} is required")
    parsed = date.fromisoformat(value)
    if parsed > date.today():
        raise ValueError(f"{field} cannot be in the future")
    return value


def enum(value: str, allowed: set[str], field: str) -> str:
    result = normalized(value)
    if result not in allowed:
        raise ValueError(f"{field} must be one of {sorted(allowed)}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--gate", default="critical,major")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.project_dir.expanduser().resolve()
    candidate_path = root / "research" / "candidates.csv"
    evidence_path = root / "research" / "evidence.csv"
    if not candidate_path.exists() or not evidence_path.exists():
        raise SystemExit("Missing research/candidates.csv or research/evidence.csv")

    candidates = load_csv(candidate_path)
    evidence = load_csv(evidence_path)
    errors: list[str] = []
    candidate_map: dict[str, dict[str, str]] = {}

    for row_number, candidate in enumerate(candidates, start=2):
        candidate_id = (candidate.get("candidate_id") or "").strip()
        name = (candidate.get("name") or "").strip()
        if not candidate_id or not name:
            errors.append(f"candidates.csv:{row_number}: candidate_id and name are required")
            continue
        if candidate_id in candidate_map:
            errors.append(f"candidates.csv:{row_number}: duplicate candidate_id {candidate_id}")
            continue
        try:
            enum(candidate.get("importance", "major"), IMPORTANCE, "importance")
            enum(candidate.get("status", "candidate"), STATUS, "status")
        except ValueError as error:
            errors.append(f"candidates.csv:{row_number}: {error}")
        candidate_map[candidate_id] = candidate

    evidence_ids: set[str] = set()
    unique_urls: set[tuple[str, str]] = set()
    fingerprints: set[tuple[str, str]] = set()
    valid_evidence: list[dict[str, str]] = []

    for row_number, item in enumerate(evidence, start=2):
        evidence_id = (item.get("evidence_id") or "").strip()
        candidate_id = (item.get("candidate_id") or "").strip()
        prefix = f"evidence.csv:{row_number}"
        if not evidence_id:
            errors.append(f"{prefix}: evidence_id is required")
            continue
        if evidence_id in evidence_ids:
            errors.append(f"{prefix}: duplicate evidence_id {evidence_id}")
            continue
        evidence_ids.add(evidence_id)
        if candidate_id not in candidate_map:
            errors.append(f"{prefix}: unknown candidate_id {candidate_id}")
            continue
        try:
            source_type = enum(item.get("source_type"), SOURCE_TYPE, "source_type")
            polarity = enum(item.get("polarity"), POLARITY, "polarity")
            relevance = enum(item.get("relevance"), RELEVANCE, "relevance")
            enum(item.get("experience_type"), EXPERIENCE_TYPE, "experience_type")
            promotion = enum(item.get("promotion"), PROMOTION, "promotion")
            identity = enum(item.get("identity_check"), IDENTITY_CHECK, "identity_check")
            valid_date(item.get("retrieved_at"), "retrieved_at")
            valid_date(item.get("published_at"), "published_at", allow_blank=True)
            url = canonical_url(item.get("url") or "")
            if not (item.get("platform") or "").strip():
                raise ValueError("platform is required")
            if not (item.get("title") or "").strip():
                raise ValueError("title is required")
            if not (item.get("claim") or "").strip():
                raise ValueError("claim is required")
            if relevance == "direct":
                if identity != "yes":
                    raise ValueError("direct evidence requires identity_check=yes")
                if source_type != "official" and not (item.get("excerpt") or "").strip():
                    raise ValueError("direct non-official evidence requires excerpt")
                if not (item.get("reviewer") or "").strip():
                    raise ValueError("direct evidence requires reviewer")
            if polarity == "official" and source_type != "official":
                raise ValueError("polarity=official requires source_type=official")
            if source_type == "official" and polarity != "official":
                raise ValueError("source_type=official requires polarity=official")
        except (ValueError, TypeError) as error:
            errors.append(f"{prefix}: {error}")
            continue

        url_key = (candidate_id, url)
        if url_key in unique_urls:
            errors.append(f"{prefix}: duplicate canonical URL for {candidate_id}: {url}")
            continue
        unique_urls.add(url_key)
        fingerprint = (item.get("content_fingerprint") or "").strip().lower()
        if fingerprint:
            fingerprint_key = (candidate_id, fingerprint)
            if fingerprint_key in fingerprints:
                errors.append(
                    f"{prefix}: duplicate content_fingerprint for {candidate_id}: {fingerprint}"
                )
                continue
            fingerprints.add(fingerprint_key)

        item["_source_type"] = source_type
        item["_polarity"] = polarity
        item["_relevance"] = relevance
        item["_promotion"] = promotion
        item["_canonical_url"] = url
        valid_evidence.append(item)

    by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in valid_evidence:
        by_candidate[(item.get("candidate_id") or "").strip()].append(item)

    lines = [
        "# Evidence coverage audit",
        "",
        "| Candidate | Importance | Positive | Negative | Official | Operational | Platforms | Result |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    failures: list[tuple[str, str, list[str]]] = []
    audited = 0

    for candidate_id, candidate in candidate_map.items():
        status = normalized(candidate.get("status", "candidate"))
        if status == "rejected":
            continue
        audited += 1
        importance = normalized(candidate.get("importance", "major"))
        defaults = DEFAULTS.get(importance, DEFAULTS["major"])
        try:
            target_fields = (
                "positive_target",
                "negative_target",
                "official_target",
                "operational_target",
                "platform_target",
            )
            targets = tuple(
                integer(candidate.get(field, ""), defaults[index])
                for index, field in enumerate(target_fields)
            )
            notes = (candidate.get("notes") or "").strip()
            for index, field in enumerate(target_fields):
                raw = (candidate.get(field) or "").strip()
                if raw and targets[index] < defaults[index]:
                    if "TARGET_OVERRIDE:" not in notes and "NOT_APPLICABLE:" not in notes:
                        raise ValueError(
                            f"{field} below the {importance} default requires "
                            "TARGET_OVERRIDE: or NOT_APPLICABLE: in notes"
                        )
        except ValueError as error:
            errors.append(f"candidate {candidate_id}: {error}")
            targets = defaults

        direct = [
            row
            for row in by_candidate.get(candidate_id, [])
            if row["_relevance"] == "direct" and row["_promotion"] == "no"
        ]
        positive = sum(row["_polarity"] == "positive" for row in direct)
        negative = sum(row["_polarity"] == "negative" for row in direct)
        official = sum(row["_source_type"] == "official" for row in direct)
        operational = sum(row["_source_type"] == "operational_failure" for row in direct)
        experiential_platforms = {
            (row.get("platform") or "").strip().lower()
            for row in direct
            if row["_polarity"] in {"positive", "negative"}
        }
        actual = (positive, negative, official, operational, len(experiential_platforms))
        labels = ("positive", "negative", "official", "operational", "platforms")
        missing = [
            f"{labels[index]} {actual[index]}/{targets[index]}"
            for index in range(5)
            if actual[index] < targets[index]
        ]
        result = "PASS" if not missing else "UNCOVERED: " + ", ".join(missing)
        if missing:
            failures.append((candidate_id, importance, missing))

        name = md_cell(candidate.get("name") or candidate_id)
        lines.append(
            f"| {name} | {importance} | {positive}/{targets[0]} | "
            f"{negative}/{targets[1]} | {official}/{targets[2]} | "
            f"{operational}/{targets[3]} | {len(experiential_platforms)}/{targets[4]} | "
            f"{result} |"
        )

    mismatch_count = sum(item["_relevance"] == "mismatch" for item in valid_evidence)
    partial_count = sum(item["_relevance"] == "partial" for item in valid_evidence)
    lines.extend(
        [
            "",
            f"- Audited candidates: {audited}",
            f"- Evidence rows: {len(evidence)}",
            f"- Valid unique evidence rows: {len(valid_evidence)}",
            f"- Explicit mismatches excluded: {mismatch_count}",
            f"- Partial records excluded from direct counts: {partial_count}",
            f"- Uncovered candidates: {len(failures)}",
            f"- Validation errors: {len(errors)}",
        ]
    )
    if errors:
        lines.extend(["", "## Validation errors", ""])
        lines.extend(f"- {error}" for error in errors)

    output = args.output or root / "research" / "analysis" / "evidence-audit.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"INVALID: {len(errors)} schema or integrity errors.")
        return 3
    gate_levels = {part.strip().lower() for part in args.gate.split(",") if part.strip()}
    gated_failures = [item for item in failures if item[1] in gate_levels]
    if gated_failures:
        for candidate_id, importance, missing in gated_failures:
            print(f"UNCOVERED: {candidate_id} ({importance}): {', '.join(missing)}")
        print(f"FAIL: {len(gated_failures)} gated candidates remain uncovered.")
        return 2
    print("PASS: no gated candidate remains uncovered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
