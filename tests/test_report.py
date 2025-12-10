"""Tests for iec62443_audit.report module.

Validates JSON export format, HTML report generation, and edge cases
like empty assessments.
"""

import json
import tempfile
import unittest
from pathlib import Path

from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult
from iec62443_audit.report import export_html, export_json, load_json


def _make_sr(sr_id: str, achieved: int, target: int = 2, notes: str = "") -> SRResult:
    return SRResult(
        sr_id=sr_id,
        sr_name=f"Test SR {sr_id}",
        sl_achieved=achieved,
        sl_target=target,
        notes=notes,
    )


def _make_fr(fr_id: str, srs: list[SRResult]) -> FRResult:
    result = FRResult(fr_id=fr_id, fr_name=f"Test FR {fr_id}", abbreviation=fr_id)
    result.sr_results = srs
    return result


def _sample_assessment() -> AssessmentResult:
    """A small but realistic assessment for testing."""
    assessment = AssessmentResult(
        system_name="Test SCADA System",
        assessor_name="Unit Tester",
        assessment_date="2025-03-10",
        sl_target=2,
    )
    assessment.fr_results = [
        _make_fr("FR1", [
            _make_sr("SR 1.1", 2, target=2),
            _make_sr("SR 1.2", 1, target=2, notes="Needs firmware update"),
        ]),
        _make_fr("FR2", [
            _make_sr("SR 2.1", 3, target=2),
        ]),
    ]
    return assessment


def _empty_assessment() -> AssessmentResult:
    """An assessment with no FR results."""
    return AssessmentResult(
        system_name="Empty System",
        assessor_name="Tester",
        assessment_date="2025-01-01",
        sl_target=2,
    )


# ---------------------------------------------------------------------------
# JSON export format
# ---------------------------------------------------------------------------

class TestJSONExport(unittest.TestCase):

    def test_export_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            self.assertTrue(path.exists())

    def test_export_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            data = json.loads(path.read_text())
            self.assertIsInstance(data, dict)

    def test_export_contains_required_top_level_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            data = json.loads(path.read_text())
            for key in [
                "system_name",
                "assessor_name",
                "assessment_date",
                "sl_target",
                "overall_sl_achieved",
                "overall_compliance_pct",
                "total_gaps",
                "foundational_requirements",
            ]:
                self.assertIn(key, data, f"Missing top-level key: {key}")

    def test_export_fr_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            data = json.loads(path.read_text())
            frs = data["foundational_requirements"]
            self.assertEqual(len(frs), 2)
            fr1 = frs[0]
            for key in [
                "fr_id", "fr_name", "abbreviation",
                "sl_achieved", "sl_target", "compliance_pct",
                "gap_count", "system_requirements",
            ]:
                self.assertIn(key, fr1, f"Missing FR key: {key}")

    def test_export_sr_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            data = json.loads(path.read_text())
            sr = data["foundational_requirements"][0]["system_requirements"][0]
            for key in ["sr_id", "sr_name", "sl_achieved", "sl_target", "gap", "compliant", "notes"]:
                self.assertIn(key, sr, f"Missing SR key: {key}")

    def test_roundtrip_via_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            original = _sample_assessment()
            export_json(original, path)
            restored = load_json(path)
            self.assertEqual(restored.system_name, original.system_name)
            self.assertEqual(restored.sl_target, original.sl_target)
            self.assertEqual(restored.overall_sl, original.overall_sl)
            self.assertEqual(restored.total_srs, original.total_srs)

    def test_notes_preserved_in_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            export_json(_sample_assessment(), path)
            data = json.loads(path.read_text())
            sr12 = data["foundational_requirements"][0]["system_requirements"][1]
            self.assertEqual(sr12["notes"], "Needs firmware update")


# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

class TestHTMLReport(unittest.TestCase):

    def test_html_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            self.assertTrue(path.exists())

    def test_html_is_not_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertGreater(len(content), 100)

    def test_html_contains_doctype(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("<!DOCTYPE html>", content)

    def test_html_contains_system_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("Test SCADA System", content)

    def test_html_contains_assessor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("Unit Tester", content)

    def test_html_contains_sl_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("SL-2", content)

    def test_html_contains_fr_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("FR1", content)
            self.assertIn("FR2", content)

    def test_html_contains_sr_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("SR 1.1", content)
            self.assertIn("SR 2.1", content)

    def test_html_contains_compliance_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            self.assertIn("Compliance", content)

    def test_html_contains_gap_info(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            export_html(_sample_assessment(), path)
            content = path.read_text()
            # The template shows "Total Gaps" in the summary
            self.assertIn("Gap", content)


# ---------------------------------------------------------------------------
# Empty assessment handling
# ---------------------------------------------------------------------------

class TestEmptyAssessmentHandling(unittest.TestCase):

    def test_empty_json_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.json"
            export_json(_empty_assessment(), path)
            data = json.loads(path.read_text())
            self.assertEqual(data["overall_sl_achieved"], 0)
            self.assertEqual(data["overall_compliance_pct"], 0.0)
            self.assertEqual(data["total_gaps"], 0)
            self.assertEqual(data["foundational_requirements"], [])

    def test_empty_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.json"
            original = _empty_assessment()
            export_json(original, path)
            restored = load_json(path)
            self.assertEqual(restored.system_name, "Empty System")
            self.assertEqual(restored.overall_sl, 0)
            self.assertEqual(restored.total_srs, 0)

    def test_empty_html_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.html"
            export_html(_empty_assessment(), path)
            content = path.read_text()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Empty System", content)


if __name__ == "__main__":
    unittest.main()
