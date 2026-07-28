#!/usr/bin/env python3
"""Audit social reputation, comment corroboration, and discrimination signals."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


COMMENT_STANCE = {
    "supports_positive",
    "supports_negative",
    "refutes_positive",
    "refutes_negative",
    "correction",
    "neutral",
}
COMMENT_EXPERIENCE = {
    "first_hand_new_fact",
    "specific_corroboration",
    "bare_agreement",
    "refutation",
    "correction",
    "merchant_response",
}
ACCESS = {"comment_opened"}
YES_NO = {"yes", "no"}
SIGNAL = {"none", "low", "medium", "high"}
INCIDENT = {"none", "vague", "specific", "concrete"}
ARTIFACT = {"none", "context", "receipt_media", "primary_record"}
DISCRIMINATION = {"d0", "d1", "d2", "d3", "not_applicable"}
SOURCE_FAMILY = {
    "china_social",
    "international_social",
    "local_social",
    "map_review",
    "official",
    "independent_blog_news",
}


@dataclass
class Cluster:
    base: float = 0.0
    comment_addition: float = 0.0
    families: set[str] = field(default_factory=set)
    months: set[str] = field(default_factory=set)
    concrete: bool = False

    @property
    def effective(self) -> float:
        return self.base + min(self.comment_addition, 0.25)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def norm(value: str) -> str:
    return (value or "").strip().lower()


def enum(value: str, allowed: set[str], field_name: str) -> str:
    result = norm(value)
    if result not in allowed:
        raise ValueError(f"{field_name} must be one of {sorted(allowed)}")
    return result


def canonical_url(value: str) -> str:
    parsed = urlsplit((value or "").strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError("permalink must be an absolute HTTP(S) URL")
    return value.strip()


def month(value: str) -> str:
    value = (value or "").strip()
    return value[:7] if len(value) >= 7 else "unknown"


def checked_date(value: str, field_name: str, allow_blank: bool = False) -> str:
    value = (value or "").strip()
    if not value and allow_blank:
        return ""
    if not value:
        raise ValueError(f"{field_name} is required")
    parsed = date.fromisoformat(value)
    if parsed > date.today():
        raise ValueError(f"{field_name} cannot be in the future")
    return value


def risk_factor(signal: str) -> float:
    return {"none": 1.0, "low": 0.75, "medium": 0.35, "high": 0.0}[signal]


def evidence_weight(row: dict[str, str], polarity: str) -> float:
    if norm(row.get("relevance")) != "direct":
        return 0.0
    if norm(row.get("access_level")) not in {"full_post_opened", "full_indexed_text"}:
        return 0.0
    if norm(row.get("identity_check")) != "yes":
        return 0.0
    experience = norm(row.get("experience_type"))
    base = {"first_hand": 1.0, "second_hand": 0.35}.get(experience, 0.0)
    if norm(row.get("access_level")) == "full_indexed_text":
        base *= 0.8
    base *= {
        "none": 0.4,
        "vague": 0.65,
        "specific": 1.0,
        "concrete": 1.15,
    }.get(norm(row.get("incident_specificity")), 0.4)
    base *= {
        "none": 1.0,
        "context": 1.05,
        "receipt_media": 1.1,
        "primary_record": 1.2,
    }.get(norm(row.get("artifact_support")), 1.0)
    promotion = norm(row.get("promotion"))
    base *= {"no": 1.0, "possible": 0.35, "yes": 0.0}.get(promotion, 0.0)
    if polarity == "positive":
        base *= risk_factor(norm(row.get("commercial_signal")))
    else:
        base *= risk_factor(norm(row.get("attack_signal")))
    return round(base, 4)


def comment_weight(row: dict[str, str], polarity: str) -> float:
    experience = norm(row.get("experience_type"))
    base = {
        "first_hand_new_fact": 0.55,
        "specific_corroboration": 0.25,
        "bare_agreement": 0.05,
        "refutation": 0.25,
        "correction": 0.35,
        "merchant_response": 0.10,
    }.get(experience, 0.0)
    base *= {
        "none": 0.5,
        "vague": 0.7,
        "specific": 1.0,
        "concrete": 1.1,
    }.get(norm(row.get("incident_specificity")), 0.5)
    if polarity == "positive":
        base *= risk_factor(norm(row.get("commercial_signal")))
    else:
        base *= risk_factor(norm(row.get("attack_signal")))
    return round(base, 4)


def limitations_complete(path: Path) -> bool:
    if not path.exists():
        return False
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ":" in line:
            values.append(line.split(":", 1)[1].strip())
    return len(values) >= 5 and sum(bool(value) for value in values) >= 5


def add_cluster(
    clusters: dict[tuple[str, str], Cluster],
    key: tuple[str, str],
    weight: float,
    family: str,
    published_at: str,
    incident: str,
    comment: bool = False,
) -> None:
    if weight <= 0:
        return
    cluster = clusters.setdefault(key, Cluster())
    if comment:
        cluster.comment_addition += weight
    else:
        cluster.base = max(cluster.base, weight)
    cluster.families.add(family)
    cluster.months.add(month(published_at))
    cluster.concrete = cluster.concrete or incident == "concrete"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.project_dir.expanduser().resolve()

    _, candidates = load_csv(root / "research" / "candidates.csv")
    _, evidence_rows = load_csv(root / "research" / "evidence.csv")
    comment_fields, comments = load_csv(root / "research" / "comments.csv")
    required_comment_fields = {
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
        "published_at",
        "retrieved_at",
        "excerpt",
        "permalink",
        "reviewer",
    }
    errors = [
        f"comments.csv: missing v1.2 column {field_name}"
        for field_name in sorted(required_comment_fields - set(comment_fields))
    ]

    candidate_map = {
        (row.get("candidate_id") or "").strip(): row
        for row in candidates
        if (row.get("candidate_id") or "").strip()
    }
    evidence_map = {
        (row.get("evidence_id") or "").strip(): row
        for row in evidence_rows
        if (row.get("evidence_id") or "").strip()
    }
    comments_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    comment_ids: set[str] = set()

    for row_number, row in enumerate(comments, start=2):
        prefix = f"comments.csv:{row_number}"
        comment_id = (row.get("comment_id") or "").strip()
        parent_id = (row.get("parent_evidence_id") or "").strip()
        candidate_id = (row.get("candidate_id") or "").strip()
        if not comment_id:
            errors.append(f"{prefix}: comment_id is required")
            continue
        if comment_id in comment_ids:
            errors.append(f"{prefix}: duplicate comment_id {comment_id}")
            continue
        comment_ids.add(comment_id)
        if parent_id not in evidence_map:
            errors.append(f"{prefix}: unknown parent_evidence_id {parent_id}")
            continue
        if candidate_id not in candidate_map:
            errors.append(f"{prefix}: unknown candidate_id {candidate_id}")
            continue
        if (evidence_map[parent_id].get("candidate_id") or "").strip() != candidate_id:
            errors.append(f"{prefix}: candidate_id does not match parent evidence")
            continue
        try:
            enum(row.get("source_family"), SOURCE_FAMILY, "source_family")
            stance = enum(row.get("stance"), COMMENT_STANCE, "stance")
            experience = enum(
                row.get("experience_type"), COMMENT_EXPERIENCE, "experience_type"
            )
            enum(row.get("access_level"), ACCESS, "access_level")
            enum(row.get("identity_check"), {"yes"}, "identity_check")
            same_incident = enum(row.get("same_incident"), YES_NO, "same_incident")
            new_fact = enum(row.get("new_fact"), YES_NO, "new_fact")
            enum(row.get("commercial_signal"), SIGNAL, "commercial_signal")
            enum(row.get("attack_signal"), SIGNAL, "attack_signal")
            incident = enum(row.get("incident_specificity"), INCIDENT, "incident_specificity")
            artifact = enum(row.get("artifact_support"), ARTIFACT, "artifact_support")
            discrimination = enum(
                row.get("discrimination_class"), DISCRIMINATION, "discrimination_class"
            )
            matched = enum(row.get("matched_comparison"), YES_NO, "matched_comparison")
            checked_date(row.get("retrieved_at") or "", "retrieved_at")
            checked_date(row.get("published_at") or "", "published_at", allow_blank=True)
            if not (row.get("platform") or "").strip():
                raise ValueError("platform is required")
            if not (row.get("independence_cluster_id") or "").strip():
                raise ValueError("independence_cluster_id is required")
            if not (row.get("excerpt") or "").strip():
                raise ValueError("excerpt is required")
            if not (row.get("reviewer") or "").strip():
                raise ValueError("reviewer is required")
            canonical_url(row.get("permalink") or "")
            if experience == "first_hand_new_fact" and new_fact != "yes":
                raise ValueError("first_hand_new_fact requires new_fact=yes")
            if experience == "bare_agreement" and new_fact != "no":
                raise ValueError("bare_agreement requires new_fact=no")
            if stance.startswith("refutes_") and experience not in {
                "refutation",
                "correction",
            }:
                raise ValueError("refuting stance requires refutation or correction")
            if same_incident == "yes" and experience == "first_hand_new_fact":
                raise ValueError(
                    "same-incident comment cannot be an independent first_hand_new_fact"
                )
            if discrimination in {"d2", "d3"}:
                if incident not in {"specific", "concrete"}:
                    raise ValueError("D2/D3 comment requires specific or concrete incident")
                if discrimination == "d2" and matched != "yes":
                    raise ValueError("D2 comment requires matched_comparison=yes")
                if discrimination == "d3" and artifact != "primary_record":
                    raise ValueError("D3 comment requires artifact_support=primary_record")
                if stance != "supports_negative":
                    raise ValueError("D2/D3 comment requires stance=supports_negative")
                if not (row.get("published_at") or "").strip():
                    raise ValueError("D2/D3 comment requires published_at")
                if not (row.get("target_group") or "").strip():
                    raise ValueError("D2/D3 comment requires target_group")
        except ValueError as error:
            errors.append(f"{prefix}: {error}")
            continue
        row["_stance"] = stance
        row["_experience"] = experience
        row["_same_incident"] = same_incident
        comments_by_candidate[candidate_id].append(row)

    if comments and not limitations_complete(root / "research" / "comment-limitations.md"):
        errors.append(
            "comment-limitations.md must disclose sampling, sorting, reply expansion, "
            "moderation/visibility limits, and comment handling"
        )

    evidence_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in evidence_rows:
        candidate_id = (row.get("candidate_id") or "").strip()
        if candidate_id in candidate_map:
            evidence_by_candidate[candidate_id].append(row)

    report = [
        "# Reputation and discrimination audit",
        "",
        "Online evidence is a non-representative independent sample. Counts below are deduplicated narrative clusters, not customers or population prevalence.",
        "",
        "| Candidate | Positive clusters / effective | Negative clusters / effective | Comment rows | Commercial-risk rows | Attack-risk rows | Discrimination | Decision |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    gate_failures: list[str] = []

    for candidate_id, candidate in candidate_map.items():
        if norm(candidate.get("status")) == "rejected":
            continue
        rows = evidence_by_candidate.get(candidate_id, [])
        candidate_comments = comments_by_candidate.get(candidate_id, [])
        clusters: dict[tuple[str, str], Cluster] = {}
        parent_cluster: dict[str, str] = {}
        d2_keys: set[str] = set()
        d2_families: set[str] = set()
        d2_months: set[str] = set()
        d3_current = False
        commercial_rows = 0
        attack_rows = 0

        for row in rows:
            discrimination = norm(row.get("discrimination_class"))
            if (
                discrimination == "d3"
                and norm(row.get("relevance")) == "direct"
                and norm(row.get("access_level"))
                in {"full_post_opened", "full_indexed_text"}
                and norm(row.get("identity_check")) == "yes"
                and norm(row.get("freshness_status")) == "current"
                and norm(row.get("artifact_support")) == "primary_record"
            ):
                d3_current = True
            polarity = norm(row.get("polarity"))
            if polarity not in {"positive", "negative"}:
                continue
            cluster_id = (row.get("independence_cluster_id") or "").strip()
            if not cluster_id:
                continue
            parent_cluster[(row.get("evidence_id") or "").strip()] = cluster_id
            family = norm(row.get("source_family"))
            weight = evidence_weight(row, polarity)
            add_cluster(
                clusters,
                (polarity, cluster_id),
                weight,
                family,
                row.get("published_at") or "",
                norm(row.get("incident_specificity")),
            )
            if norm(row.get("commercial_signal")) in {"medium", "high"}:
                commercial_rows += 1
            if norm(row.get("attack_signal")) in {"medium", "high"}:
                attack_rows += 1
            if discrimination == "d2" and weight > 0:
                d2_keys.add(cluster_id)
                d2_families.add(family)
                d2_months.add(month(row.get("published_at") or ""))

        for row in candidate_comments:
            stance = row["_stance"]
            if stance in {"supports_positive", "refutes_negative"}:
                polarity = "positive"
            elif stance in {"supports_negative", "refutes_positive"}:
                polarity = "negative"
            else:
                continue
            cluster_id = (row.get("independence_cluster_id") or "").strip()
            same_incident = row["_same_incident"] == "yes"
            if same_incident:
                cluster_id = parent_cluster.get(
                    (row.get("parent_evidence_id") or "").strip(), cluster_id
                )
            family = norm(row.get("source_family"))
            weight = comment_weight(row, polarity)
            add_cluster(
                clusters,
                (polarity, cluster_id),
                weight,
                family,
                row.get("published_at") or "",
                norm(row.get("incident_specificity")),
                comment=same_incident,
            )
            if norm(row.get("commercial_signal")) in {"medium", "high"}:
                commercial_rows += 1
            if norm(row.get("attack_signal")) in {"medium", "high"}:
                attack_rows += 1
            discrimination = norm(row.get("discrimination_class"))
            if discrimination == "d3" and norm(row.get("artifact_support")) == "primary_record":
                d3_current = True
            if discrimination == "d2" and weight > 0 and not same_incident:
                d2_keys.add(cluster_id)
                d2_families.add(family)
                d2_months.add(month(row.get("published_at") or ""))

        positive = {
            key[1]: value for key, value in clusters.items() if key[0] == "positive"
        }
        negative = {
            key[1]: value for key, value in clusters.items() if key[0] == "negative"
        }
        pos_effective = sum(item.effective for item in positive.values())
        neg_effective = sum(item.effective for item in negative.values())
        concrete_negative = sum(item.concrete for item in negative.values())
        d2_converged = (
            len(d2_keys) >= 3 and len(d2_families) >= 2 and len(d2_months) >= 2
        )

        if d3_current:
            discrimination_result = "D3 current primary artifact"
            decision = "AVOID_REVIEW"
        elif d2_converged:
            discrimination_result = (
                f"D2 convergence {len(d2_keys)} clusters/"
                f"{len(d2_families)} families/{len(d2_months)} windows"
            )
            decision = "AVOID_REVIEW"
        elif d2_keys:
            discrimination_result = f"D2 monitor: {len(d2_keys)} independent clusters"
            decision = "CAUTION"
        else:
            discrimination_result = "No convergent D2/D3 signal"
            if (
                len(negative) >= 3
                and concrete_negative >= 2
                and neg_effective >= max(3.0, pos_effective * 2)
            ):
                decision = "AVOID_REVIEW"
            elif len(negative) >= 2 and neg_effective >= pos_effective * 1.35:
                decision = "CAUTION"
            elif len(positive) >= 2 and pos_effective >= max(1.0, neg_effective * 1.5):
                decision = "FAVORABLE_WITH_CAVEATS"
            else:
                decision = "MIXED_OR_INSUFFICIENT"

        required = norm(candidate.get("reputation_required")) == "yes"
        if required and (not positive or not negative):
            gate_failures.append(
                f"{candidate_id}: reputation_required needs eligible positive and negative clusters"
            )

        report.append(
            f"| {(candidate.get('name') or candidate_id).replace('|', '/')} | "
            f"{len(positive)} / {pos_effective:.2f} | "
            f"{len(negative)} / {neg_effective:.2f} | {len(candidate_comments)} | "
            f"{commercial_rows} | {attack_rows} | {discrimination_result} | {decision} |"
        )

    report.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- `AVOID_REVIEW` means the planner must conservatively reassess or avoid the scoped branch; it is not a legal finding.",
            "- D0 ordinary rudeness and D1 ambiguous treatment do not count toward the discrimination gate.",
            "- A word such as “骗局/scam” is only an allegation unless the record describes a concrete operational pattern.",
            "- Bare agreement and emoji comments are weak sentiment and capped; same-incident comments never become independent incidents.",
            "- Merchant replies, substantive refutations, corrections, and visibility limitations remain in the record.",
            "",
            f"- Comment rows audited: {len(comments)}",
            f"- Validation errors: {len(errors)}",
            f"- Reputation gate failures: {len(gate_failures)}",
        ]
    )
    if errors:
        report.extend(["", "## Validation errors", ""])
        report.extend(f"- {item}" for item in errors)
    if gate_failures:
        report.extend(["", "## Gate failures", ""])
        report.extend(f"- {item}" for item in gate_failures)

    output = args.output or root / "research" / "analysis" / "reputation-audit.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(output)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 3
    if gate_failures:
        for item in gate_failures:
            print(f"UNCOVERED: {item}")
        return 2
    print("PASS: reputation and comment audit completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
