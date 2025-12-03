"""Multi-zone assessment for IEC 62443.

Supports assessing multiple zones and conduits separately, then
aggregating into a site-level view.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from iec62443_audit.scoring import AssessmentResult


@dataclass
class ZoneDefinition:
    """Definition of a security zone or conduit."""

    name: str
    zone_type: str = "zone"  # zone, conduit
    description: str = ""
    sl_target: int = 2
    parent_zone: str = ""
    connected_zones: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    criticality: str = "medium"  # low, medium, high, critical

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "zone_type": self.zone_type,
            "description": self.description,
            "sl_target": self.sl_target,
            "parent_zone": self.parent_zone,
            "connected_zones": self.connected_zones,
            "assets": self.assets,
            "criticality": self.criticality,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoneDefinition":
        return cls(
            name=data["name"],
            zone_type=data.get("zone_type", "zone"),
            description=data.get("description", ""),
            sl_target=data.get("sl_target", 2),
            parent_zone=data.get("parent_zone", ""),
            connected_zones=data.get("connected_zones", []),
            assets=data.get("assets", []),
            criticality=data.get("criticality", "medium"),
        )


@dataclass
class ZoneAssessment:
    """An assessment result tied to a specific zone."""

    zone: ZoneDefinition
    assessment: AssessmentResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone": self.zone.to_dict(),
            "assessment": self.assessment.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoneAssessment":
        return cls(
            zone=ZoneDefinition.from_dict(data["zone"]),
            assessment=AssessmentResult.from_dict(data["assessment"]),
        )


@dataclass
class SiteAssessment:
    """Aggregated assessment across all zones at a site."""

    site_name: str
    zone_assessments: List[ZoneAssessment] = field(default_factory=list)

    @property
    def zone_count(self) -> int:
        return len(self.zone_assessments)

    @property
    def overall_sl(self) -> int:
        """Site-level SL is the minimum across all zones."""
        if not self.zone_assessments:
            return 0
        return min(za.assessment.overall_sl for za in self.zone_assessments)

    @property
    def overall_compliance_pct(self) -> float:
        """Average compliance across all zones."""
        if not self.zone_assessments:
            return 0.0
        return sum(
            za.assessment.overall_compliance_pct for za in self.zone_assessments
        ) / len(self.zone_assessments)

    @property
    def total_gaps(self) -> int:
        return sum(za.assessment.total_gaps for za in self.zone_assessments)

    @property
    def weakest_zone(self) -> Optional[ZoneAssessment]:
        """Return the zone with the lowest SL."""
        if not self.zone_assessments:
            return None
        return min(self.zone_assessments, key=lambda za: za.assessment.overall_sl)

    def get_zone(self, zone_name: str) -> Optional[ZoneAssessment]:
        """Find a zone assessment by name."""
        for za in self.zone_assessments:
            if za.zone.name == zone_name:
                return za
        return None

    def add_zone(self, zone_assessment: ZoneAssessment) -> None:
        """Add or replace a zone assessment."""
        existing = self.get_zone(zone_assessment.zone.name)
        if existing:
            self.zone_assessments.remove(existing)
        self.zone_assessments.append(zone_assessment)

    def zone_summary(self) -> List[Dict[str, Any]]:
        """Summary of all zones for reporting."""
        return [
            {
                "name": za.zone.name,
                "type": za.zone.zone_type,
                "criticality": za.zone.criticality,
                "sl_target": za.zone.sl_target,
                "sl_achieved": za.assessment.overall_sl,
                "compliance_pct": round(za.assessment.overall_compliance_pct, 1),
                "gaps": za.assessment.total_gaps,
            }
            for za in self.zone_assessments
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "site_name": self.site_name,
            "zone_count": self.zone_count,
            "overall_sl": self.overall_sl,
            "overall_compliance_pct": round(self.overall_compliance_pct, 1),
            "total_gaps": self.total_gaps,
            "zone_assessments": [za.to_dict() for za in self.zone_assessments],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SiteAssessment":
        site = cls(site_name=data["site_name"])
        for za_data in data.get("zone_assessments", []):
            site.zone_assessments.append(ZoneAssessment.from_dict(za_data))
        return site
