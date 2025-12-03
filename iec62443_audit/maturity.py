"""Maturity model for IEC 62443 implementation tracking.

Tracks implementation maturity per SR using a five-level model:
Not Started -> Planned -> In Progress -> Implemented -> Verified
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional


class MaturityLevel(IntEnum):
    """Implementation maturity levels for an SR."""

    NOT_STARTED = 0
    PLANNED = 1
    IN_PROGRESS = 2
    IMPLEMENTED = 3
    VERIFIED = 4

    @property
    def label(self) -> str:
        return {
            0: "Not Started",
            1: "Planned",
            2: "In Progress",
            3: "Implemented",
            4: "Verified",
        }[self.value]

    @property
    def color(self) -> str:
        """Rich color for display."""
        return {
            0: "red",
            1: "yellow",
            2: "blue",
            3: "green",
            4: "bold green",
        }[self.value]

    @property
    def symbol(self) -> str:
        return {
            0: "[ ]",
            1: "[P]",
            2: "[~]",
            3: "[+]",
            4: "[*]",
        }[self.value]


@dataclass
class MaturityRecord:
    """Maturity tracking for a single SR."""

    sr_id: str
    level: MaturityLevel = MaturityLevel.NOT_STARTED
    owner: str = ""
    notes: str = ""
    target_date: str = ""
    completion_date: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sr_id": self.sr_id,
            "level": self.level.value,
            "level_label": self.level.label,
            "owner": self.owner,
            "notes": self.notes,
            "target_date": self.target_date,
            "completion_date": self.completion_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaturityRecord":
        return cls(
            sr_id=data.get("sr_id", ""),
            level=MaturityLevel(data.get("level", 0)),
            owner=data.get("owner", ""),
            notes=data.get("notes", ""),
            target_date=data.get("target_date", ""),
            completion_date=data.get("completion_date", ""),
        )


class MaturityTracker:
    """Tracks maturity across all SRs in an assessment."""

    def __init__(self) -> None:
        self._records: Dict[str, MaturityRecord] = {}

    def set_maturity(
        self,
        sr_id: str,
        level: MaturityLevel,
        owner: str = "",
        notes: str = "",
        target_date: str = "",
    ) -> MaturityRecord:
        """Set or update maturity for an SR."""
        record = self._records.get(sr_id, MaturityRecord(sr_id=sr_id))
        record.level = level
        if owner:
            record.owner = owner
        if notes:
            record.notes = notes
        if target_date:
            record.target_date = target_date
        self._records[sr_id] = record
        return record

    def get(self, sr_id: str) -> Optional[MaturityRecord]:
        """Get maturity record for an SR."""
        return self._records.get(sr_id)

    def get_or_default(self, sr_id: str) -> MaturityRecord:
        """Get maturity record, creating a default if needed."""
        if sr_id not in self._records:
            self._records[sr_id] = MaturityRecord(sr_id=sr_id)
        return self._records[sr_id]

    @property
    def records(self) -> Dict[str, MaturityRecord]:
        return dict(self._records)

    def count_by_level(self) -> Dict[MaturityLevel, int]:
        """Count SRs at each maturity level."""
        counts: Dict[MaturityLevel, int] = {level: 0 for level in MaturityLevel}
        for record in self._records.values():
            counts[record.level] += 1
        return counts

    @property
    def overall_maturity_score(self) -> float:
        """Average maturity score (0.0 to 4.0)."""
        if not self._records:
            return 0.0
        return sum(r.level.value for r in self._records.values()) / len(self._records)

    @property
    def verified_pct(self) -> float:
        """Percentage of SRs at Verified level."""
        if not self._records:
            return 0.0
        verified = sum(1 for r in self._records.values() if r.level == MaturityLevel.VERIFIED)
        return (verified / len(self._records)) * 100

    @property
    def implemented_or_above_pct(self) -> float:
        """Percentage of SRs at Implemented or Verified."""
        if not self._records:
            return 0.0
        count = sum(
            1
            for r in self._records.values()
            if r.level >= MaturityLevel.IMPLEMENTED
        )
        return (count / len(self._records)) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            sr_id: record.to_dict()
            for sr_id, record in self._records.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaturityTracker":
        tracker = cls()
        for sr_id, record_data in data.items():
            tracker._records[sr_id] = MaturityRecord.from_dict(record_data)
        return tracker
