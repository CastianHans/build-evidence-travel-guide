#!/usr/bin/env python3
"""Audit candidate-level travel evidence using full-read, cluster-aware gates."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


DEFAULTS = {
    "critical": (2, 2, 1, 1, 2),
    "major": (2, 2, 1, 0, 2),
    "minor": (1, 1, 0, 0, 1),
}
IMPORTANCE = set(DEFAULTS)
STATUS = {"candidate", "included", "optional", "rejected"}
SOURCE_FAMILY = {
    "china_social",
    "international_social",
    "local_social",
    "map_review",
    "official",
    "independent_blog_news",
}
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
ACCESS_LEVEL = {
    "full_post_opened",
    "full_indexed_text",
    "comment_opened",
    "search_snippet",
    "title_only",
}
DIRECT_ACCESS = {"full_post_opened", "full_indexed_text"}
EXPERIENCE_TYPE = {
    "first_hand",
    "official",
    "second_hand",
}
PROMOTION = {"no", "possible", "yes"}
SIGNAL = {"none", "low", "medium", "high"}
IDENTITY_CHECK = {"yes", "no", "unknown"}
INCIDENT_SPECIFICITY = {"none", "vague", "specific", "concrete"}
ARTIFACT_SUPPORT = {"none", "context", "receipt_media", "primary_record"}
DISCRIMINATION_CLASS = {"d0", "d1", "d2", "d3", "not_applicable"}
YES_NO = {"yes", "no"}
FRESHNESS = {"current", "stale", "not_applicable"}
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


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


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


def required_columns(actual: list[str], expected: set[str], label: str) -> list[str]:
    missing = sorted(expected - set(actual))
    return [f"{label}: missing v1.2 column {item}" for item in missing]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--gate", default="critical,major")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--official-max-age-days", type=int, default=45)
    args = parser.parse_args()

    root = args.project_dir.expanduser().resolve()
    candidate_path = root / "research" / "candidates.csv"
    evidence_path = root / "research" / "evidence.csv"
    if not candidate_path.exists() or not evidence_path.exists():
        raise SystemExit("Missing research/candidates.csv or research/evidence.csv")

    candidate_fields, candidates = load_csv(candidate_path)
    evidence_fields, evidence = load_csv(evidence_path)
    errors = required_columns(
        candidate_fields,
        {
            "candidate_id",
            "name",
            "importance",
            "status",
            "source_family_target",
            "reputation_required",
            "rejection_reason",
            "replacement_candidate_id",
        },
        "candidates.csv",
    )
    errors.extend(
        required_columns(
            evidence_fields,
            {
                "evidence_id",
                "candidate_id",
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
                "independence_cluster_id",
                "incident_specificity",
                "artifact_support",
                "discrimination_class",
                "matched_comparison",
                "freshness_status",
                "retrieved_at",
                "title",
                "claim",
                "url",
                "reviewer",
            },
            "evidence.csv",
        )
    )
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
            status = enum(candidate.get("status", "candidate"), STATUS, "status")
            enum(candidate.get("reputation_required", "no"), YES_NO, "reputation_required")
            if status == "rejected" and not (candidate.get("rejection_reason") or "").strip():
                raise ValueError("rejected candidate requires rejection_reason")
        except ValueError as error:
            errors.append(f"candidates.csv:{row_number}: {error}")
        candidate_map[candidate_id] = candidate

    evidence_ids: set[str] = set()
    unique_urls: set[tuple[str, str]] = set()
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
            source_family = enum(item.get("source_family"), SOURCE_FAMILY, "source_family")
            source_type = enum(item.get("source_type"), SOURCE_TYPE, "source_type")
            polarity = enum(item.get("polarity"), POLARITY, "polarity")
            relevance = enum(item.get("relevance"), RELEVANCE, "relevance")
            access_level = enum(item.get("access_level"), ACCESS_LEVEL, "access_level")
            experience_type = enum(
                item.get("experience_type"), EXPERIENCE_TYPE, "experience_type"
            )
            promotion = enum(item.get("promotion"), PROMOTION, "promotion")
            commercial_signal = enum(
                item.get("commercial_signal"), SIGNAL, "commercial_signal"
            )
            attack_signal = enum(item.get("attack_signal"), SIGNAL, "attack_signal")
            identity = enum(item.get("identity_check"), IDENTITY_CHECK, "identity_check")
            incident = enum(
                item.get("incident_specificity"), INCIDENT_SPECIFICITY, "incident_specificity"
            )
            artifact = enum(item.get("artifact_support"), ARTIFACT_SUPPORT, "artifact_support")
            discrimination = enum(
                item.get("discrimination_class"),
                DISCRIMINATION_CLASS,
                "discrimination_class",
            )
            matched = enum(item.get("matched_comparison"), YES_NO, "matched_comparison")
            freshness = enum(item.get("freshness_status"), FRESHNESS, "freshness_status")
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
                if access_level not in DIRECT_ACCESS:
                    raise ValueError(
                        "direct evidence requires full_post_opened or full_indexed_text"
                    )
                if identity != "yes":
                    raise ValueError("direct evidence requires identity_check=yes")
                if source_type != "official" and not (item.get("excerpt") or "").strip():
                    raise ValueError("direct non-official evidence requires excerpt")
                if not (item.get("reviewer") or "").strip():
                    raise ValueError("direct evidence requires reviewer")
            if polarity == "official" and source_type != "official":
                raise ValueError("polarity=official requires source_type=official")
            if source_type == "official":
                if polarity != "official" or source_family != "official":
                    raise ValueError(
                        "official source requires polarity=official and source_family=official"
                    )
                if experience_type != "official":
                    raise ValueError("official source requires experience_type=official")
                if relevance == "direct" and freshness != "current":
                    raise ValueError("direct official evidence requires freshness_status=current")
                retrieved = date.fromisoformat((item.get("retrieved_at") or "").strip())
                if (
                    relevance == "direct"
                    and retrieved < date.today() - timedelta(days=args.official_max_age_days)
                ):
                    raise ValueError(
                        "direct official evidence is stale; retrieve it again or adjust "
                        "--official-max-age-days with a documented reason"
                    )
            elif source_family == "official":
                raise ValueError("source_family=official requires source_type=official")
            if source_type == "social" and source_family not in {
                "china_social",
                "international_social",
                "local_social",
            }:
                raise ValueError("source_type=social requires a social source_family")
            if source_type == "map_review" and source_family != "map_review":
                raise ValueError("source_type=map_review requires source_family=map_review")
            if source_type in {"blog", "news"} and source_family != "independent_blog_news":
                raise ValueError(
                    "blog/news requires source_family=independent_blog_news"
                )
            if source_type == "operational_failure" and polarity != "negative":
                raise ValueError("operational_failure requires polarity=negative")
            if relevance == "direct" and source_type != "official":
                if not (item.get("independence_cluster_id") or "").strip():
                    raise ValueError(
                        "direct experiential evidence requires independence_cluster_id"
                    )
            if discrimination in {"d2", "d3"}:
                if incident not in {"specific", "concrete"}:
                    raise ValueError("D2/D3 evidence requires specific or concrete incident")
                if discrimination == "d2" and matched != "yes":
                    raise ValueError("D2 evidence requires matched_comparison=yes")
                if discrimination == "d3" and artifact != "primary_record":
                    raise ValueError("D3 evidence requires artifact_support=primary_record")
                if discrimination == "d2" and polarity != "negative":
                    raise ValueError("D2 evidence requires polarity=negative")
                if discrimination == "d3" and polarity not in {"negative", "official"}:
                    raise ValueError("D3 evidence requires polarity=negative or official")
                if not (item.get("published_at") or "").strip():
                    raise ValueError("D2/D3 evidence requires published_at")
                if not (item.get("target_group") or "").strip():
                    raise ValueError("D2/D3 evidence requires target_group")
            candidate_branch = (
                candidate_map[candidate_id].get("branch_or_variant") or ""
            ).strip()
            evidence_branch = (item.get("branch_or_variant") or "").strip()
            if relevance == "direct" and candidate_branch:
                if not evidence_branch:
                    raise ValueError(
                        "direct evidence requires branch_or_variant for this candidate"
                    )
                if normalized(evidence_branch) != normalized(candidate_branch):
                    raise ValueError(
                        "direct evidence branch_or_variant does not match candidate"
                    )
            if promotion == "yes" and commercial_signal == "none":
                raise ValueError("promotion=yes requires a commercial_signal")
        except (ValueError, TypeError) as error:
            errors.append(f"{prefix}: {error}")
            continue

        url_key = (candidate_id, url)
        if url_key in unique_urls:
            errors.append(f"{prefix}: duplicate canonical URL for {candidate_id}: {url}")
            continue
        unique_urls.add(url_key)

        item["_source_family"] = source_family
        item["_source_type"] = source_type
        item["_polarity"] = polarity
        item["_relevance"] = relevance
        item["_access_level"] = access_level
        item["_promotion"] = promotion
        item["_commercial_signal"] = commercial_signal
        item["_attack_signal"] = attack_signal
        item["_canonical_url"] = url
        valid_evidence.append(item)

    by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in valid_evidence:
        by_candidate[(item.get("candidate_id") or "").strip()].append(item)

    lines = [
        "# Evidence coverage audit",
        "",
        "Counts are independent content clusters, not raw posts.",
        "",
        "| Candidate | Importance | Positive | Negative | Official | Operational | Source families | Result |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    failures: list[tuple[str, str, list[str]]] = []
    audited = 0

    for candidate_id, candidate in candidate_map.items():
        status = normalized(candidate.get("status", "candidate"))
        rows = by_candidate.get(candidate_id, [])
        if status == "rejected":
            reason = (candidate.get("rejection_reason") or "").strip()
            replacement = (candidate.get("replacement_candidate_id") or "").strip()
            has_direct_basis = any(row["_relevance"] == "direct" for row in rows)
            preference_basis = reason.startswith("USER_PREFERENCE:")
            if replacement and replacement not in candidate_map:
                errors.append(
                    f"candidate {candidate_id}: unknown replacement_candidate_id {replacement}"
                )
            if not has_direct_basis and not preference_basis:
                errors.append(
                    f"candidate {candidate_id}: rejected status requires direct evidence "
                    "or USER_PREFERENCE: in rejection_reason"
                )
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
                "source_family_target",
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

        eligible = [
            row
            for row in rows
            if row["_relevance"] == "direct"
            and row["_access_level"] in DIRECT_ACCESS
            and row["_promotion"] == "no"
        ]
        positive_clusters = {
            row.get("independence_cluster_id", "")
            for row in eligible
            if row["_polarity"] == "positive"
            and row["_commercial_signal"] not in {"medium", "high"}
        }
        negative_clusters = {
            row.get("independence_cluster_id", "")
            for row in eligible
            if row["_polarity"] == "negative"
            and row["_attack_signal"] not in {"medium", "high"}
        }
        official_urls = {
            row["_canonical_url"]
            for row in eligible
            if row["_source_type"] == "official"
            and normalized(row.get("freshness_status")) == "current"
        }
        operational_clusters = {
            row.get("independence_cluster_id", "")
            for row in eligible
            if row["_source_type"] == "operational_failure"
            and row["_attack_signal"] not in {"medium", "high"}
        }
        experiential_families = {
            row["_source_family"]
            for row in eligible
            if row["_polarity"] in {"positive", "negative"}
            and row["_source_family"] != "official"
        }
        actual = (
            len(positive_clusters),
            len(negative_clusters),
            len(official_urls),
            len(operational_clusters),
            len(experiential_families),
        )
        labels = ("positive", "negative", "official", "operational", "source_families")
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
            f"| {name} | {importance} | {actual[0]}/{targets[0]} | "
            f"{actual[1]}/{targets[1]} | {actual[2]}/{targets[2]} | "
            f"{actual[3]}/{targets[3]} | {actual[4]}/{targets[4]} | {result} |"
        )

    mismatch_count = sum(item["_relevance"] == "mismatch" for item in valid_evidence)
    partial_count = sum(item["_relevance"] == "partial" for item in valid_evidence)
    snippet_count = sum(
        item["_access_level"] in {"search_snippet", "title_only"} for item in valid_evidence
    )
    lines.extend(
        [
            "",
            f"- Audited candidates: {audited}",
            f"- Evidence rows: {len(evidence)}",
            f"- Structurally valid unique rows: {len(valid_evidence)}",
            f"- Search-snippet/title-only rows excluded: {snippet_count}",
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
