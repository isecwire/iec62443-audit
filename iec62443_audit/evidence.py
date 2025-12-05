"""Evidence collection for IEC 62443 assessments.

Allows attaching evidence notes, screenshot references, document links,
and other supporting materials to each SR/CR assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceItem:
    """A single piece of evidence attached to an SR assessment."""

    type: str  # "note", "screenshot", "document", "url", "observation"
    description: str
    reference: str = ""  # file path, URL, document ID
    collected_by: str = ""
    collected_date: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "reference": self.reference,
            "collected_by": self.collected_by,
            "collected_date": self.collected_date,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceItem":
        return cls(
            type=data.get("type", "note"),
            description=data.get("description", ""),
            reference=data.get("reference", ""),
            collected_by=data.get("collected_by", ""),
            collected_date=data.get("collected_date", ""),
            tags=data.get("tags", []),
        )


@dataclass
class EvidenceCollection:
    """Collection of evidence items for a single SR/CR."""

    sr_id: str
    items: List[EvidenceItem] = field(default_factory=list)
    overall_confidence: str = "low"  # low, medium, high

    def add_note(
        self,
        description: str,
        collected_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> EvidenceItem:
        """Add a text note as evidence."""
        item = EvidenceItem(
            type="note",
            description=description,
            collected_by=collected_by,
            collected_date=datetime.now().isoformat(),
            tags=tags or [],
        )
        self.items.append(item)
        return item

    def add_document(
        self,
        description: str,
        reference: str,
        collected_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> EvidenceItem:
        """Add a document reference as evidence."""
        item = EvidenceItem(
            type="document",
            description=description,
            reference=reference,
            collected_by=collected_by,
            collected_date=datetime.now().isoformat(),
            tags=tags or [],
        )
        self.items.append(item)
        return item

    def add_screenshot(
        self,
        description: str,
        reference: str,
        collected_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> EvidenceItem:
        """Add a screenshot reference as evidence."""
        item = EvidenceItem(
            type="screenshot",
            description=description,
            reference=reference,
            collected_by=collected_by,
            collected_date=datetime.now().isoformat(),
            tags=tags or [],
        )
        self.items.append(item)
        return item

    def add_url(
        self,
        description: str,
        url: str,
        collected_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> EvidenceItem:
        """Add a URL reference as evidence."""
        item = EvidenceItem(
            type="url",
            description=description,
            reference=url,
            collected_by=collected_by,
            collected_date=datetime.now().isoformat(),
            tags=tags or [],
        )
        self.items.append(item)
        return item

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def has_evidence(self) -> bool:
        return len(self.items) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sr_id": self.sr_id,
            "overall_confidence": self.overall_confidence,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceCollection":
        coll = cls(
            sr_id=data.get("sr_id", ""),
            overall_confidence=data.get("overall_confidence", "low"),
        )
        for item_data in data.get("items", []):
            coll.items.append(EvidenceItem.from_dict(item_data))
        return coll


class EvidenceStore:
    """Central store for all evidence across an assessment."""

    def __init__(self) -> None:
        self._collections: Dict[str, EvidenceCollection] = {}

    def get_or_create(self, sr_id: str) -> EvidenceCollection:
        """Get existing or create new evidence collection for an SR."""
        if sr_id not in self._collections:
            self._collections[sr_id] = EvidenceCollection(sr_id=sr_id)
        return self._collections[sr_id]

    def get(self, sr_id: str) -> Optional[EvidenceCollection]:
        """Get evidence collection for an SR, or None."""
        return self._collections.get(sr_id)

    def all_collections(self) -> Dict[str, EvidenceCollection]:
        """Return all evidence collections."""
        return dict(self._collections)

    @property
    def total_items(self) -> int:
        return sum(c.count for c in self._collections.values())

    @property
    def srs_with_evidence(self) -> int:
        return sum(1 for c in self._collections.values() if c.has_evidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            sr_id: coll.to_dict()
            for sr_id, coll in self._collections.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceStore":
        store = cls()
        for sr_id, coll_data in data.items():
            store._collections[sr_id] = EvidenceCollection.from_dict(coll_data)
        return store
