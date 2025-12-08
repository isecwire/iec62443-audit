"""Tests for iec62443_audit.scoring module.

Validates SL-Achieved calculation, compliance percentages, gap analysis,
JSON serialization roundtrip, and assessment comparison logic.
"""

import unittest

from iec62443_audit.scoring import (
    AssessmentResult,
    FRResult,
    SRResult,
    compare_assessments,
)


def _make_sr(sr_id: str, achieved: int, target: int = 2, notes: str = "") -> SRResult:
    """Helper to create an SRResult with minimal boilerplate."""
    return SRResult(
        sr_id=sr_id,
        sr_name=f"Test SR {sr_id}",
        sl_achieved=achieved,
        sl_target=target,
        notes=notes,
    )


def _make_fr(fr_id: str, srs: list[SRResult]) -> FRResult:
    """Helper to create an FRResult."""
    result = FRResult(fr_id=fr_id, fr_name=f"Test FR {fr_id}", abbreviation=fr_id)
    result.sr_results = srs
    return result


def _make_assessment(
    fr_data: list[tuple[str, list[tuple[str, int]]]],
    target: int = 2,
) -> AssessmentResult:
    """Build a full AssessmentResult from compact data.

    fr_data: list of (fr_id, [(sr_id, sl_achieved), ...])
    """
    result = AssessmentResult(
        system_name="Test System",
        assessor_name="Tester",
        assessment_date="2025-01-15",
        sl_target=target,
    )
    for fr_id, srs in fr_data:
        sr_results = [_make_sr(sr_id, achieved, target) for sr_id, achieved in srs]
        result.fr_results.append(_make_fr(fr_id, sr_results))
    return result


# ---------------------------------------------------------------------------
# SRResult
# ---------------------------------------------------------------------------

class TestSRResult(unittest.TestCase):

    def test_gap_positive_when_below_target(self):
        sr = _make_sr("SR 1.1", achieved=1, target=3)
        self.assertEqual(sr.gap, 2)

    def test_gap_zero_when_meets_target(self):
        sr = _make_sr("SR 1.1", achieved=2, target=2)
        self.assertEqual(sr.gap, 0)

    def test_gap_zero_when_exceeds_target(self):
        sr = _make_sr("SR 1.1", achieved=4, target=2)
        self.assertEqual(sr.gap, 0)

    def test_compliant_true(self):
        sr = _make_sr("SR 1.1", achieved=2, target=2)
        self.assertTrue(sr.compliant)

    def test_compliant_false(self):
        sr = _make_sr("SR 1.1", achieved=1, target=2)
        self.assertFalse(sr.compliant)


# ---------------------------------------------------------------------------
# FRResult -- SL-Achieved per FR (minimum of SRs)
# ---------------------------------------------------------------------------

class TestFRResultSLAchieved(unittest.TestCase):

    def test_sl_achieved_is_minimum_of_srs(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 3),
            _make_sr("SR 1.2", 1),
            _make_sr("SR 1.3", 4),
        ])
        self.assertEqual(fr.sl_achieved, 1)

    def test_sl_achieved_all_same(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 2),
            _make_sr("SR 1.2", 2),
        ])
        self.assertEqual(fr.sl_achieved, 2)

    def test_sl_achieved_empty_srs(self):
        fr = _make_fr("FR1", [])
        self.assertEqual(fr.sl_achieved, 0)

    def test_sl_achieved_single_sr(self):
        fr = _make_fr("FR1", [_make_sr("SR 1.1", 3)])
        self.assertEqual(fr.sl_achieved, 3)


# ---------------------------------------------------------------------------
# FRResult -- Compliance percentage
# ---------------------------------------------------------------------------

class TestFRCompliancePercentage(unittest.TestCase):

    def test_all_compliant(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 2, target=2),
            _make_sr("SR 1.2", 3, target=2),
        ])
        self.assertAlmostEqual(fr.compliance_pct, 100.0)

    def test_none_compliant(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 0, target=2),
            _make_sr("SR 1.2", 1, target=2),
        ])
        self.assertAlmostEqual(fr.compliance_pct, 0.0)

    def test_partial_compliance(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 2, target=2),
            _make_sr("SR 1.2", 0, target=2),
            _make_sr("SR 1.3", 3, target=2),
            _make_sr("SR 1.4", 1, target=2),
        ])
        # 2 of 4 compliant = 50%
        self.assertAlmostEqual(fr.compliance_pct, 50.0)

    def test_empty_srs_returns_zero(self):
        fr = _make_fr("FR1", [])
        self.assertAlmostEqual(fr.compliance_pct, 0.0)


# ---------------------------------------------------------------------------
# AssessmentResult -- Overall SL and compliance
# ---------------------------------------------------------------------------

class TestOverallSL(unittest.TestCase):

    def test_overall_sl_is_minimum_of_frs(self):
        assessment = _make_assessment([
            ("FR1", [("SR 1.1", 3)]),
            ("FR2", [("SR 2.1", 1)]),
            ("FR3", [("SR 3.1", 4)]),
        ])
        self.assertEqual(assessment.overall_sl, 1)

    def test_overall_sl_empty(self):
        assessment = AssessmentResult(
            system_name="Empty",
            assessor_name="T",
            assessment_date="2025-01-01",
            sl_target=2,
        )
        self.assertEqual(assessment.overall_sl, 0)

    def test_overall_compliance_pct(self):
        assessment = _make_assessment([
            ("FR1", [("SR 1.1", 2), ("SR 1.2", 0)]),
            ("FR2", [("SR 2.1", 3), ("SR 2.2", 2)]),
        ])
        # 3 of 4 compliant = 75%
        self.assertAlmostEqual(assessment.overall_compliance_pct, 75.0)

    def test_total_gaps(self):
        assessment = _make_assessment([
            ("FR1", [("SR 1.1", 2), ("SR 1.2", 0)]),
            ("FR2", [("SR 2.1", 1)]),
        ])
        # SR 1.2 (gap=2) and SR 2.1 (gap=1) => 2 gaps
        self.assertEqual(assessment.total_gaps, 2)

    def test_total_srs(self):
        assessment = _make_assessment([
            ("FR1", [("SR 1.1", 2), ("SR 1.2", 0)]),
            ("FR2", [("SR 2.1", 1)]),
        ])
        self.assertEqual(assessment.total_srs, 3)


# ---------------------------------------------------------------------------
# Gap analysis (target - achieved)
# ---------------------------------------------------------------------------

class TestGapAnalysis(unittest.TestCase):

    def test_gap_per_sr(self):
        sr = _make_sr("SR 1.1", achieved=0, target=3)
        self.assertEqual(sr.gap, 3)

    def test_gap_count_on_fr(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 2, target=2),
            _make_sr("SR 1.2", 1, target=2),
            _make_sr("SR 1.3", 0, target=2),
        ])
        self.assertEqual(fr.gap_count, 2)

    def test_no_gaps_when_all_meet_target(self):
        fr = _make_fr("FR1", [
            _make_sr("SR 1.1", 2, target=2),
            _make_sr("SR 1.2", 4, target=2),
        ])
        self.assertEqual(fr.gap_count, 0)


# ---------------------------------------------------------------------------
# JSON serialization / deserialization roundtrip
# ---------------------------------------------------------------------------

class TestSerializationRoundtrip(unittest.TestCase):

    def _sample_assessment(self) -> AssessmentResult:
        return _make_assessment([
            ("FR1", [("SR 1.1", 2), ("SR 1.2", 1)]),
            ("FR2", [("SR 2.1", 3)]),
        ])

    def test_to_dict_keys(self):
        d = self._sample_assessment().to_dict()
        self.assertIn("system_name", d)
        self.assertIn("sl_target", d)
        self.assertIn("overall_sl_achieved", d)
        self.assertIn("overall_compliance_pct", d)
        self.assertIn("foundational_requirements", d)

    def test_roundtrip_preserves_system_name(self):
        original = self._sample_assessment()
        restored = AssessmentResult.from_dict(original.to_dict())
        self.assertEqual(restored.system_name, original.system_name)

    def test_roundtrip_preserves_sl_target(self):
        original = self._sample_assessment()
        restored = AssessmentResult.from_dict(original.to_dict())
        self.assertEqual(restored.sl_target, original.sl_target)

    def test_roundtrip_preserves_sr_data(self):
        original = self._sample_assessment()
        restored = AssessmentResult.from_dict(original.to_dict())
        self.assertEqual(restored.total_srs, original.total_srs)
        orig_sr = original.fr_results[0].sr_results[0]
        rest_sr = restored.fr_results[0].sr_results[0]
        self.assertEqual(rest_sr.sr_id, orig_sr.sr_id)
        self.assertEqual(rest_sr.sl_achieved, orig_sr.sl_achieved)

    def test_roundtrip_preserves_overall_sl(self):
        original = self._sample_assessment()
        restored = AssessmentResult.from_dict(original.to_dict())
        self.assertEqual(restored.overall_sl, original.overall_sl)

    def test_roundtrip_preserves_notes(self):
        assessment = AssessmentResult(
            system_name="NoteTest",
            assessor_name="T",
            assessment_date="2025-01-01",
            sl_target=2,
        )
        fr = _make_fr("FR1", [_make_sr("SR 1.1", 2, notes="check firmware")])
        assessment.fr_results.append(fr)
        restored = AssessmentResult.from_dict(assessment.to_dict())
        self.assertEqual(
            restored.fr_results[0].sr_results[0].notes,
            "check firmware",
        )


# ---------------------------------------------------------------------------
# Compare assessments (improvement / regression detection)
# ---------------------------------------------------------------------------

class TestCompareAssessments(unittest.TestCase):

    def _baseline(self) -> AssessmentResult:
        return _make_assessment([
            ("FR1", [("SR 1.1", 1), ("SR 1.2", 2)]),
            ("FR2", [("SR 2.1", 2)]),
        ])

    def _current_improved(self) -> AssessmentResult:
        return _make_assessment([
            ("FR1", [("SR 1.1", 3), ("SR 1.2", 2)]),
            ("FR2", [("SR 2.1", 2)]),
        ])

    def _current_regressed(self) -> AssessmentResult:
        return _make_assessment([
            ("FR1", [("SR 1.1", 1), ("SR 1.2", 0)]),
            ("FR2", [("SR 2.1", 2)]),
        ])

    def test_improvement_detected(self):
        comp = compare_assessments(self._baseline(), self._current_improved())
        self.assertGreater(comp["overall_sl_delta"], 0)
        # Find SR 1.1 delta
        fr1 = comp["foundational_requirements"][0]
        sr11 = next(sr for sr in fr1["system_requirements"] if sr["sr_id"] == "SR 1.1")
        self.assertEqual(sr11["status"], "improved")
        self.assertEqual(sr11["delta"], 2)

    def test_regression_detected(self):
        comp = compare_assessments(self._baseline(), self._current_regressed())
        fr1 = comp["foundational_requirements"][0]
        sr12 = next(sr for sr in fr1["system_requirements"] if sr["sr_id"] == "SR 1.2")
        self.assertEqual(sr12["status"], "regressed")
        self.assertEqual(sr12["delta"], -2)

    def test_unchanged_detected(self):
        comp = compare_assessments(self._baseline(), self._baseline())
        self.assertEqual(comp["overall_sl_delta"], 0)
        for fr in comp["foundational_requirements"]:
            for sr in fr["system_requirements"]:
                self.assertEqual(sr["status"], "unchanged")

    def test_comparison_dates(self):
        baseline = self._baseline()
        current = self._current_improved()
        current.assessment_date = "2025-06-01"
        comp = compare_assessments(baseline, current)
        self.assertEqual(comp["baseline_date"], "2025-01-15")
        self.assertEqual(comp["current_date"], "2025-06-01")

    def test_compliance_delta(self):
        comp = compare_assessments(self._baseline(), self._current_improved())
        # baseline: SR 1.1=1 (gap), SR 1.2=2 (ok), SR 2.1=2 (ok) => 66.7%
        # current:  SR 1.1=3 (ok),  SR 1.2=2 (ok), SR 2.1=2 (ok) => 100%
        self.assertGreater(comp["compliance_delta"], 0)


if __name__ == "__main__":
    unittest.main()
