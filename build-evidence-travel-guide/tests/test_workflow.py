from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"

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
TRACE_FIELDS = [
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


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def candidate(**overrides: str) -> dict[str, str]:
    row = {field: "" for field in CANDIDATE_FIELDS}
    row.update(
        {
            "candidate_id": "c1",
            "name": "Example Pass",
            "category": "transit_pass",
            "importance": "critical",
            "status": "included",
            "positive_target": "1",
            "negative_target": "1",
            "official_target": "1",
            "operational_target": "1",
            "source_family_target": "2",
            "reputation_required": "yes",
            "notes": "TARGET_OVERRIDE: compact deterministic test fixture",
        }
    )
    row.update(overrides)
    return row


def evidence(evidence_id: str, **overrides: str) -> dict[str, str]:
    row = {field: "" for field in EVIDENCE_FIELDS}
    row.update(
        {
            "evidence_id": evidence_id,
            "candidate_id": "c1",
            "platform": "Xiaohongshu",
            "source_family": "china_social",
            "source_type": "social",
            "polarity": "positive",
            "relevance": "direct",
            "access_level": "full_post_opened",
            "experience_type": "first_hand",
            "promotion": "no",
            "commercial_signal": "none",
            "attack_signal": "none",
            "identity_check": "yes",
            "branch_or_variant": "main branch",
            "independence_cluster_id": evidence_id,
            "incident_specificity": "specific",
            "artifact_support": "context",
            "discrimination_class": "not_applicable",
            "matched_comparison": "no",
            "published_at": "2025-01-01",
            "retrieved_at": date.today().isoformat(),
            "freshness_status": "not_applicable",
            "title": "Example",
            "claim": "Concrete claim",
            "excerpt": "Concrete excerpt about the exact candidate.",
            "url": f"https://example.com/{evidence_id}",
            "reviewer": "tester",
        }
    )
    row.update(overrides)
    return row


def comment(comment_id: str, **overrides: str) -> dict[str, str]:
    row = {field: "" for field in COMMENT_FIELDS}
    row.update(
        {
            "comment_id": comment_id,
            "parent_evidence_id": "p1",
            "candidate_id": "c1",
            "platform": "Xiaohongshu",
            "source_family": "china_social",
            "stance": "supports_positive",
            "experience_type": "bare_agreement",
            "access_level": "comment_opened",
            "identity_check": "yes",
            "same_incident": "yes",
            "new_fact": "no",
            "independence_cluster_id": "p1",
            "commercial_signal": "none",
            "attack_signal": "none",
            "incident_specificity": "vague",
            "artifact_support": "none",
            "discrimination_class": "not_applicable",
            "matched_comparison": "no",
            "published_at": "2025-01-02",
            "retrieved_at": "2026-01-01",
            "excerpt": "同意",
            "permalink": f"https://example.com/comments/{comment_id}",
            "reviewer": "tester",
        }
    )
    row.update(overrides)
    return row


def official(evidence_id: str = "o1") -> dict[str, str]:
    return evidence(
        evidence_id,
        platform="Official operator",
        source_family="official",
        source_type="official",
        polarity="official",
        experience_type="official",
        independence_cluster_id="",
        incident_specificity="none",
        artifact_support="primary_record",
        excerpt="",
        freshness_status="current",
    )


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(
            [sys.executable, str(SCRIPTS / "init_project.py"), str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), str(self.root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def write_research(
        self,
        candidates: list[dict[str, str]],
        evidence_rows: list[dict[str, str]],
        comments: list[dict[str, str]] | None = None,
    ) -> None:
        write_csv(self.root / "research" / "candidates.csv", CANDIDATE_FIELDS, candidates)
        write_csv(self.root / "research" / "evidence.csv", EVIDENCE_FIELDS, evidence_rows)
        write_csv(
            self.root / "research" / "comments.csv",
            COMMENT_FIELDS,
            comments or [],
        )

    def valid_rows(self) -> list[dict[str, str]]:
        return [
            evidence("p1"),
            evidence(
                "n1",
                platform="Reddit",
                source_family="international_social",
                source_type="operational_failure",
                polarity="negative",
            ),
            official(),
        ]

    def fill_comment_limitations(self) -> None:
        (self.root / "research" / "comment-limitations.md").write_text(
            """# Comment evidence limitations
- Platforms/comments inspected: Xiaohongshu test fixture
- Sort order or sampling method: top and newest
- Whether replies were expanded: yes
- Known moderation, deletion, login, rate-limit, or visibility limits: unknown deletion
- How same-incident, copied, bare-agreement, merchant, and suspected coordinated comments were handled: clustered and capped
- Reviewer and review time: tester 2026-01-01
""",
            encoding="utf-8",
        )

    def test_init_creates_all_v12_ledgers(self) -> None:
        expected = [
            "requirements/traceability.csv",
            "research/candidates.csv",
            "research/evidence.csv",
            "research/comments.csv",
            "research/comment-limitations.md",
            "work/itinerary.csv",
            "work/run-state.json",
        ]
        self.assertTrue(all((self.root / item).exists() for item in expected))
        state = json.loads((self.root / "work" / "run-state.json").read_text())
        self.assertEqual(state["schema_version"], "1.2")

    def test_valid_clustered_multifamily_evidence_passes(self) -> None:
        self.write_research([candidate()], self.valid_rows())
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_search_snippet_cannot_be_direct_evidence(self) -> None:
        rows = self.valid_rows()
        rows[0]["access_level"] = "search_snippet"
        self.write_research([candidate()], rows)
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("direct evidence requires full_post_opened", result.stdout)

    def test_same_cluster_does_not_double_count(self) -> None:
        rows = [
            evidence("p1", independence_cluster_id="copy"),
            evidence(
                "p2",
                independence_cluster_id="copy",
                url="https://another.example/copy",
            ),
        ]
        self.write_research(
            [
                candidate(
                    positive_target="2",
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    source_family_target="1",
                )
            ],
            rows,
        )
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive 1/2", result.stdout)

    def test_duplicate_canonical_url_is_invalid(self) -> None:
        rows = [
            evidence("p1", url="https://example.com/post?utm_source=a"),
            evidence("p2", url="https://example.com/post?utm_source=b"),
        ]
        self.write_research(
            [
                candidate(
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    source_family_target="1",
                )
            ],
            rows,
        )
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("duplicate canonical URL", result.stdout)

    def test_commercial_risk_blocks_positive_coverage(self) -> None:
        self.write_research(
            [
                candidate(
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    source_family_target="0",
                )
            ],
            [evidence("p1", commercial_signal="high")],
        )
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive 0/1", result.stdout)

    def test_stale_official_check_is_invalid(self) -> None:
        rows = self.valid_rows()
        rows[2]["retrieved_at"] = "2025-01-01"
        self.write_research([candidate()], rows)
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("direct official evidence is stale", result.stdout)

    def test_rejected_candidate_needs_evidence_or_user_preference(self) -> None:
        rejected = candidate(
            status="rejected",
            rejection_reason="route is weak",
            reputation_required="no",
        )
        self.write_research([rejected], [])
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("rejected status requires direct evidence", result.stdout)

    def test_user_preference_can_reject_without_research(self) -> None:
        rejected = candidate(
            status="rejected",
            rejection_reason="USER_PREFERENCE: user does not want museums",
            reputation_required="no",
        )
        self.write_research([rejected], [])
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_d2_requires_matched_comparison(self) -> None:
        rows = self.valid_rows()
        rows[1].update(
            {
                "discrimination_class": "d2",
                "incident_specificity": "concrete",
                "matched_comparison": "no",
                "target_group": "Chinese travelers",
            }
        )
        self.write_research([candidate()], rows)
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("D2 evidence requires matched_comparison=yes", result.stdout)

    def test_d3_requires_primary_record(self) -> None:
        rows = self.valid_rows()
        rows[1].update(
            {
                "discrimination_class": "d3",
                "incident_specificity": "concrete",
                "artifact_support": "receipt_media",
                "target_group": "Chinese travelers",
            }
        )
        self.write_research([candidate()], rows)
        result = self.run_script("audit_evidence.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("D3 evidence requires artifact_support=primary_record", result.stdout)

    def test_reputation_required_needs_both_sides(self) -> None:
        self.write_research([candidate()], [evidence("p1")])
        result = self.run_script("audit_reputation.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("needs eligible positive and negative clusters", result.stdout)

    def test_same_incident_comment_cannot_claim_new_independent_event(self) -> None:
        self.fill_comment_limitations()
        bad_comment = comment(
            "cm1",
            experience_type="first_hand_new_fact",
            new_fact="yes",
            same_incident="yes",
        )
        self.write_research([candidate()], self.valid_rows(), [bad_comment])
        result = self.run_script("audit_reputation.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("same-incident comment cannot be", result.stdout)

    def test_comment_limitations_are_mandatory(self) -> None:
        self.write_research([candidate()], self.valid_rows(), [comment("cm1")])
        result = self.run_script("audit_reputation.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("comment-limitations.md must disclose", result.stdout)

    def test_cross_family_cross_window_d2_convergence_flags_avoid_review(self) -> None:
        negatives = [
            evidence(
                "n1",
                polarity="negative",
                source_family="china_social",
                discrimination_class="d2",
                matched_comparison="yes",
                incident_specificity="concrete",
                target_group="Chinese travelers",
                published_at="2025-01-01",
            ),
            evidence(
                "n2",
                polarity="negative",
                platform="Reddit",
                source_family="international_social",
                discrimination_class="d2",
                matched_comparison="yes",
                incident_specificity="concrete",
                target_group="Chinese travelers",
                published_at="2025-03-01",
            ),
            evidence(
                "n3",
                polarity="negative",
                platform="Naver",
                source_family="local_social",
                discrimination_class="d2",
                matched_comparison="yes",
                incident_specificity="concrete",
                target_group="Chinese travelers",
                published_at="2025-04-01",
            ),
        ]
        self.write_research([candidate()], [evidence("p1"), *negatives])
        result = self.run_script("audit_reputation.py")
        self.assertEqual(result.returncode, 0, result.stdout)
        report = (self.root / "research" / "analysis" / "reputation-audit.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("D2 convergence 3 clusters/3 families/3 windows", report)
        self.assertIn("AVOID_REVIEW", report)

    def test_valid_hotel_anchored_itinerary_passes(self) -> None:
        candidates = [
            candidate(
                candidate_id="hotel",
                name="Exact Hotel",
                category="hotel",
                reputation_required="no",
            ),
            candidate(
                candidate_id="stop",
                name="Museum",
                category="attraction",
                reputation_required="no",
            ),
        ]
        write_csv(self.root / "research" / "candidates.csv", CANDIDATE_FIELDS, candidates)
        rows = [
            self.itinerary_row(
                sequence="1",
                candidate_id="hotel",
                stop_name="Hotel departure",
                start_time="08:00",
                end_time="08:30",
                activity_minutes="30",
                hotel_start="yes",
            ),
            self.itinerary_row(
                sequence="2",
                candidate_id="stop",
                stop_name="Museum",
                start_time="08:30",
                end_time="10:00",
                transit_minutes="30",
                activity_minutes="60",
            ),
            self.itinerary_row(
                sequence="3",
                candidate_id="hotel",
                stop_name="Hotel return",
                start_time="10:00",
                end_time="10:30",
                transit_minutes="30",
                activity_minutes="0",
                hotel_return="yes",
            ),
        ]
        write_csv(self.root / "work" / "itinerary.csv", ITINERARY_FIELDS, rows)
        result = self.run_script("audit_itinerary.py")
        self.assertEqual(result.returncode, 0, result.stdout)

    def itinerary_row(self, **overrides: str) -> dict[str, str]:
        row = {field: "" for field in ITINERARY_FIELDS}
        row.update(
            {
                "day_id": "D1",
                "sequence": "1",
                "candidate_id": "c1",
                "stop_name": "Stop",
                "start_time": "08:00",
                "end_time": "08:30",
                "transit_minutes": "0",
                "search_buffer_minutes": "0",
                "activity_minutes": "30",
                "meal_rest_minutes": "0",
                "contingency_minutes": "0",
                "mode": "walk",
                "route_detail": "Exact route instruction",
                "hotel_start": "no",
                "hotel_return": "no",
                "fallback_day_id": "D1-R",
            }
        )
        row.update(overrides)
        return row

    def test_itinerary_time_mismatch_is_invalid(self) -> None:
        write_csv(
            self.root / "research" / "candidates.csv",
            CANDIDATE_FIELDS,
            [candidate(reputation_required="no")],
        )
        write_csv(
            self.root / "work" / "itinerary.csv",
            ITINERARY_FIELDS,
            [
                self.itinerary_row(
                    activity_minutes="10", hotel_start="yes", hotel_return="yes"
                )
            ],
        )
        result = self.run_script("audit_itinerary.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("time arithmetic mismatch", result.stdout)

    def test_traceability_blocks_required_gap_in_final_mode(self) -> None:
        write_csv(
            self.root / "research" / "candidates.csv",
            CANDIDATE_FIELDS,
            [candidate(reputation_required="no")],
        )
        trace = {field: "" for field in TRACE_FIELDS}
        trace.update(
            {
                "requirement_id": "r1",
                "source": "user_confirmed",
                "requirement": "Must include the pass",
                "required": "yes",
                "candidate_ids": "c1",
                "status": "declared_gap",
                "notes": "not researched yet",
            }
        )
        write_csv(
            self.root / "requirements" / "traceability.csv", TRACE_FIELDS, [trace]
        )
        result = self.run_script("audit_traceability.py", "--mode", "final")
        self.assertEqual(result.returncode, 2)
        self.assertIn("required requirements are not satisfied", result.stdout)

    def test_provisional_finalizer_never_marks_final_on_missing_gates(self) -> None:
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest("reportlab unavailable")
        pdf = self.root / "draft_v0.1.pdf"
        drawing = canvas.Canvas(str(pdf))
        drawing.drawString(72, 720, "Draft travel guide v0.1")
        drawing.save()
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "finalize_run.py"),
                str(self.root),
                str(pdf),
                "--mode",
                "provisional",
                "--document-version",
                "v0.1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads(
            (self.root / "work" / "finalization-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["status"], "provisional")
        self.assertFalse(manifest["final_allowed"])

    def test_complete_fixture_can_reach_final_state(self) -> None:
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest("reportlab unavailable")
        self.write_research(
            [candidate(name="Exact Hotel", category="hotel")], self.valid_rows()
        )
        trace = {field: "" for field in TRACE_FIELDS}
        trace.update(
            {
                "requirement_id": "r1",
                "source": "acceptance",
                "requirement": "Complete executable day",
                "required": "yes",
                "candidate_ids": "c1",
                "pdf_section": "Day 1",
                "status": "satisfied",
                "verification": "fixture",
            }
        )
        write_csv(
            self.root / "requirements" / "traceability.csv", TRACE_FIELDS, [trace]
        )
        itinerary = [
            self.itinerary_row(
                sequence="1",
                stop_name="Hotel departure",
                start_time="08:00",
                end_time="08:30",
                activity_minutes="30",
                hotel_start="yes",
            ),
            self.itinerary_row(
                sequence="2",
                stop_name="Main stop",
                start_time="08:30",
                end_time="10:00",
                transit_minutes="30",
                activity_minutes="60",
            ),
            self.itinerary_row(
                sequence="3",
                stop_name="Hotel return",
                start_time="10:00",
                end_time="10:30",
                transit_minutes="30",
                activity_minutes="0",
                hotel_return="yes",
            ),
        ]
        write_csv(
            self.root / "work" / "itinerary.csv", ITINERARY_FIELDS, itinerary
        )
        pdf = self.root / "guide_v1.0.pdf"
        drawing = canvas.Canvas(str(pdf))
        drawing.setTitle("Fixture guide")
        drawing.drawString(72, 760, "Weather - checked 2026-01-01")
        drawing.drawString(72, 740, "Pre-departure preparation")
        drawing.drawString(72, 720, "Document version v1.0")
        drawing.drawString(72, 700, "Evidence ledger: 3 rows")
        drawing.drawString(72, 680, "Candidates: 1 item")
        drawing.drawString(72, 660, "Day 1 complete route")
        drawing.save()
        page_image = self.root / "work" / "page-1.png"
        page_image.write_bytes(b"fixture")
        visual = self.root / "work" / "visual-inspection.csv"
        write_csv(
            visual,
            ["page", "image", "status", "inspector", "inspected_at", "notes"],
            [
                {
                    "page": "1",
                    "image": str(page_image),
                    "status": "pass",
                    "inspector": "tester",
                    "inspected_at": "2026-01-01T10:00:00+00:00",
                    "notes": "full-page fixture inspection",
                }
            ],
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "finalize_run.py"),
                str(self.root),
                str(pdf),
                "--document-version",
                "v1.0",
                "--visual-manifest",
                str(visual),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads(
            (self.root / "work" / "finalization-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["status"], "final")
        self.assertTrue(manifest["final_allowed"])

    def test_skill_has_valid_frontmatter_and_no_placeholders(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: build-evidence-travel-guide\n"))
        self.assertNotIn("TODO", text)
        self.assertNotIn("PLACEHOLDER", text)
        self.assertLess(len(text.splitlines()), 500)


if __name__ == "__main__":
    unittest.main()
