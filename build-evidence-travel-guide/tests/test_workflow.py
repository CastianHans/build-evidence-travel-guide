from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"

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
            "platform_target": "2",
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
            "source_type": "social",
            "polarity": "positive",
            "relevance": "direct",
            "experience_type": "first_hand",
            "promotion": "no",
            "identity_check": "yes",
            "published_at": "2025-01-01",
            "retrieved_at": "2026-01-01",
            "title": "Example",
            "claim": "Concrete claim",
            "excerpt": "Concrete excerpt about the exact candidate.",
            "url": f"https://example.com/{evidence_id}",
            "reviewer": "tester",
        }
    )
    row.update(overrides)
    return row


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

    def run_audit(
        self, candidates: list[dict[str, str]], evidence_rows: list[dict[str, str]]
    ) -> subprocess.CompletedProcess[str]:
        write_csv(self.root / "research" / "candidates.csv", CANDIDATE_FIELDS, candidates)
        write_csv(self.root / "research" / "evidence.csv", EVIDENCE_FIELDS, evidence_rows)
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "audit_evidence.py"), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_unique_multiplatform_evidence_passes(self) -> None:
        rows = [
            evidence("p1"),
            evidence(
                "n1",
                platform="Reddit",
                source_type="operational_failure",
                polarity="negative",
            ),
            evidence(
                "o1",
                platform="Official",
                source_type="official",
                polarity="official",
                experience_type="official",
                excerpt="",
            ),
        ]
        result = self.run_audit([candidate()], rows)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_canonical_url_is_invalid(self) -> None:
        rows = [
            evidence("p1", url="https://example.com/post?utm_source=a"),
            evidence("p2", url="https://example.com/post?utm_source=b"),
        ]
        result = self.run_audit(
            [
                candidate(
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    platform_target="1",
                )
            ],
            rows,
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("duplicate canonical URL", result.stdout + result.stderr)

    def test_duplicate_evidence_id_is_invalid(self) -> None:
        result = self.run_audit(
            [candidate(negative_target="0", official_target="0", operational_target="0")],
            [evidence("same"), evidence("same", url="https://example.com/other")],
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("duplicate evidence_id", result.stdout + result.stderr)

    def test_orphan_evidence_is_invalid(self) -> None:
        result = self.run_audit(
            [candidate()],
            [evidence("orphan", candidate_id="missing")],
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("unknown candidate_id", result.stdout + result.stderr)

    def test_mismatch_does_not_satisfy_negative_gate(self) -> None:
        rows = [
            evidence("p1"),
            evidence(
                "n1",
                platform="Reddit",
                polarity="negative",
                relevance="mismatch",
                identity_check="no",
            ),
            evidence(
                "o1",
                platform="Official",
                source_type="official",
                polarity="official",
                experience_type="official",
                excerpt="",
            ),
        ]
        result = self.run_audit(
            [candidate(operational_target="0", platform_target="1")],
            rows,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("negative 0/1", result.stdout + result.stderr)

    def test_possible_promotion_does_not_count(self) -> None:
        result = self.run_audit(
            [
                candidate(
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    platform_target="1",
                )
            ],
            [evidence("p1", promotion="possible")],
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive 0/1", result.stdout + result.stderr)

    def test_lowered_target_requires_written_reason(self) -> None:
        result = self.run_audit(
            [
                candidate(
                    negative_target="0",
                    official_target="0",
                    operational_target="0",
                    notes="",
                )
            ],
            [evidence("p1")],
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("requires TARGET_OVERRIDE", result.stdout + result.stderr)

    def test_direct_social_requires_excerpt_and_identity_check(self) -> None:
        result = self.run_audit(
            [candidate()],
            [evidence("bad", excerpt="", identity_check="unknown")],
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("identity_check=yes", result.stdout + result.stderr)

    def test_skill_has_valid_frontmatter_and_no_placeholders(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: build-evidence-travel-guide\n"))
        self.assertNotIn("TODO", text)
        self.assertNotIn("PLACEHOLDER", text)


if __name__ == "__main__":
    unittest.main()
