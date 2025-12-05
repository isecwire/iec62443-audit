"""Scoring and gap analysis for IEC 62443 assessments.

Computes SL-Achieved per FR, overall SL, gap analysis, weighted compliance
percentages, and risk-based prioritization from a completed assessment.
Supports both IEC 62443-3-3 and IEC 62443-4-2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from iec62443_audit.requirements import (
    FOUNDATIONAL_REQUIREMENTS,
    FoundationalRequirement,
)


@dataclass
class SRResult:
    """Result for a single system requirement."""

    sr_id: str
    sr_name: str
    sl_achieved: int  # 0-4
    sl_target: int  # 1-4
    notes: str = ""
    business_impact: float = 1.0  # weight 0.0-3.0 for risk-based scoring
    maturity: int = 0  # 0=Not Started, 1=Planned, 2=In Progress, 3=Implemented, 4=Verified
    evidence_refs: List[str] = field(default_factory=list)

    @property
    def gap(self) -> int:
        """Gap between target and achieved (positive = shortfall)."""
        return max(0, self.sl_target - self.sl_achieved)

    @property
    def compliant(self) -> bool:
        return self.sl_achieved >= self.sl_target

    @property
    def weighted_gap(self) -> float:
        """Gap weighted by business impact."""
        return self.gap * self.business_impact

    @property
    def risk_score(self) -> float:
        """Risk score: higher = worse. Gap * impact weight."""
        return self.gap * self.business_impact


@dataclass
class FRResult:
    """Aggregated result for a foundational requirement."""

    fr_id: str
    fr_name: str
    abbreviation: str
    sr_results: List[SRResult] = field(default_factory=list)

    @property
    def sl_achieved(self) -> int:
        """SL-Achieved for this FR is the minimum across all SRs.

        Per IEC 62443 methodology, the achieved security level for a
        foundational requirement equals the lowest SL achieved by any
        of its constituent system requirements.
        """
        if not self.sr_results:
            return 0
        return min(sr.sl_achieved for sr in self.sr_results)

    @property
    def sl_achieved_avg(self) -> float:
        """Average SL-Achieved across SRs (useful for reporting)."""
        if not self.sr_results:
            return 0.0
        return sum(sr.sl_achieved for sr in self.sr_results) / len(self.sr_results)

    @property
    def sl_target(self) -> int:
        """SL-Target for this FR is the max target across SRs."""
        if not self.sr_results:
            return 0
        return max(sr.sl_target for sr in self.sr_results)

    @property
    def compliance_pct(self) -> float:
        """Percentage of SRs meeting or exceeding their target."""
        if not self.sr_results:
            return 0.0
        compliant = sum(1 for sr in self.sr_results if sr.compliant)
        return (compliant / len(self.sr_results)) * 100

    @property
    def gap_count(self) -> int:
        """Number of SRs with a gap."""
        return sum(1 for sr in self.sr_results if sr.gap > 0)

    @property
    def weighted_compliance_pct(self) -> float:
        """Weighted compliance: SRs with higher business impact weigh more."""
        if not self.sr_results:
            return 0.0
        total_weight = sum(sr.business_impact for sr in self.sr_results)
        if total_weight == 0:
            return 0.0
        compliant_weight = sum(
            sr.business_impact for sr in self.sr_results if sr.compliant
        )
        return (compliant_weight / total_weight) * 100

    @property
    def total_risk_score(self) -> float:
        """Sum of risk scores across all SRs in this FR."""
        return sum(sr.risk_score for sr in self.sr_results)


@dataclass
class AssessmentResult:
    """Full assessment result across all foundational requirements."""

    system_name: str
    assessor_name: str
    assessment_date: str
    sl_target: int
    fr_results: List[FRResult] = field(default_factory=list)

    @property
    def overall_sl(self) -> int:
        """Overall SL-Achieved is the minimum across all FRs."""
        if not self.fr_results:
            return 0
        return min(fr.sl_achieved for fr in self.fr_results)

    @property
    def overall_compliance_pct(self) -> float:
        """Overall compliance percentage across all SRs."""
        total_srs = sum(len(fr.sr_results) for fr in self.fr_results)
        if total_srs == 0:
            return 0.0
        compliant = sum(
            sum(1 for sr in fr.sr_results if sr.compliant)
            for fr in self.fr_results
        )
        return (compliant / total_srs) * 100

    @property
    def total_gaps(self) -> int:
        return sum(fr.gap_count for fr in self.fr_results)

    @property
    def total_srs(self) -> int:
        return sum(len(fr.sr_results) for fr in self.fr_results)

    @property
    def overall_risk_score(self) -> float:
        """Total risk score across all FRs."""
        return sum(fr.total_risk_score for fr in self.fr_results)

    @property
    def weighted_compliance_pct(self) -> float:
        """Overall weighted compliance across all SRs."""
        total_weight = sum(
            sr.business_impact
            for fr in self.fr_results
            for sr in fr.sr_results
        )
        if total_weight == 0:
            return 0.0
        compliant_weight = sum(
            sr.business_impact
            for fr in self.fr_results
            for sr in fr.sr_results
            if sr.compliant
        )
        return (compliant_weight / total_weight) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        return {
            "system_name": self.system_name,
            "assessor_name": self.assessor_name,
            "assessment_date": self.assessment_date,
            "sl_target": self.sl_target,
            "overall_sl_achieved": self.overall_sl,
            "overall_compliance_pct": round(self.overall_compliance_pct, 1),
            "overall_risk_score": round(self.overall_risk_score, 2),
            "total_gaps": self.total_gaps,
            "foundational_requirements": [
                {
                    "fr_id": fr.fr_id,
                    "fr_name": fr.fr_name,
                    "abbreviation": fr.abbreviation,
                    "sl_achieved": fr.sl_achieved,
                    "sl_achieved_avg": round(fr.sl_achieved_avg, 2),
                    "sl_target": fr.sl_target,
                    "compliance_pct": round(fr.compliance_pct, 1),
                    "weighted_compliance_pct": round(fr.weighted_compliance_pct, 1),
                    "gap_count": fr.gap_count,
                    "risk_score": round(fr.total_risk_score, 2),
                    "system_requirements": [
                        {
                            "sr_id": sr.sr_id,
                            "sr_name": sr.sr_name,
                            "sl_achieved": sr.sl_achieved,
                            "sl_target": sr.sl_target,
                            "gap": sr.gap,
                            "compliant": sr.compliant,
                            "notes": sr.notes,
                            "business_impact": sr.business_impact,
                            "maturity": sr.maturity,
                            "evidence_refs": sr.evidence_refs,
                        }
                        for sr in fr.sr_results
                    ],
                }
                for fr in self.fr_results
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssessmentResult":
        """Deserialize from a JSON-compatible dict."""
        result = cls(
            system_name=data["system_name"],
            assessor_name=data["assessor_name"],
            assessment_date=data["assessment_date"],
            sl_target=data["sl_target"],
        )
        for fr_data in data["foundational_requirements"]:
            fr_result = FRResult(
                fr_id=fr_data["fr_id"],
                fr_name=fr_data["fr_name"],
                abbreviation=fr_data["abbreviation"],
            )
            for sr_data in fr_data["system_requirements"]:
                fr_result.sr_results.append(
                    SRResult(
                        sr_id=sr_data["sr_id"],
                        sr_name=sr_data["sr_name"],
                        sl_achieved=sr_data["sl_achieved"],
                        sl_target=sr_data["sl_target"],
                        notes=sr_data.get("notes", ""),
                        business_impact=sr_data.get("business_impact", 1.0),
                        maturity=sr_data.get("maturity", 0),
                        evidence_refs=sr_data.get("evidence_refs", []),
                    )
                )
            result.fr_results.append(fr_result)
        return result


def compare_assessments(
    baseline: AssessmentResult,
    current: AssessmentResult,
) -> Dict[str, Any]:
    """Compare two assessments and return a progress summary.

    Returns a dict with per-FR and per-SR deltas showing improvement,
    regression, or no change.
    """
    comparison: Dict[str, Any] = {
        "baseline_date": baseline.assessment_date,
        "current_date": current.assessment_date,
        "system_name": current.system_name,
        "overall_sl_baseline": baseline.overall_sl,
        "overall_sl_current": current.overall_sl,
        "overall_sl_delta": current.overall_sl - baseline.overall_sl,
        "compliance_baseline": round(baseline.overall_compliance_pct, 1),
        "compliance_current": round(current.overall_compliance_pct, 1),
        "compliance_delta": round(
            current.overall_compliance_pct - baseline.overall_compliance_pct, 1
        ),
        "foundational_requirements": [],
    }

    baseline_map = {fr.fr_id: fr for fr in baseline.fr_results}
    current_map = {fr.fr_id: fr for fr in current.fr_results}

    for fr_id in sorted(set(list(baseline_map.keys()) + list(current_map.keys()))):
        b_fr = baseline_map.get(fr_id)
        c_fr = current_map.get(fr_id)
        if not b_fr or not c_fr:
            continue

        b_sr_map = {sr.sr_id: sr for sr in b_fr.sr_results}
        c_sr_map = {sr.sr_id: sr for sr in c_fr.sr_results}

        sr_deltas = []
        for sr_id in sorted(set(list(b_sr_map.keys()) + list(c_sr_map.keys()))):
            b_sr = b_sr_map.get(sr_id)
            c_sr = c_sr_map.get(sr_id)
            if not b_sr or not c_sr:
                continue
            delta = c_sr.sl_achieved - b_sr.sl_achieved
            sr_deltas.append({
                "sr_id": sr_id,
                "sr_name": c_sr.sr_name,
                "baseline": b_sr.sl_achieved,
                "current": c_sr.sl_achieved,
                "delta": delta,
                "status": (
                    "improved" if delta > 0
                    else "regressed" if delta < 0
                    else "unchanged"
                ),
            })

        comparison["foundational_requirements"].append({
            "fr_id": fr_id,
            "fr_name": c_fr.fr_name,
            "sl_baseline": b_fr.sl_achieved,
            "sl_current": c_fr.sl_achieved,
            "sl_delta": c_fr.sl_achieved - b_fr.sl_achieved,
            "compliance_baseline": round(b_fr.compliance_pct, 1),
            "compliance_current": round(c_fr.compliance_pct, 1),
            "system_requirements": sr_deltas,
        })

    return comparison
