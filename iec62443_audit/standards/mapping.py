"""Cross-standard mapping: IEC 62443 SRs/CRs to NIST CSF, ISO 27001, CIS Controls.

Also includes regulatory mapping to EU CRA, NIS2, and GDPR articles
where applicable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StandardMapping:
    """Mapping of a single IEC 62443 requirement to other standards."""

    iec62443_id: str  # e.g. "SR 1.1" or "CR 1.1"
    nist_csf: List[str] = field(default_factory=list)
    iso27001: List[str] = field(default_factory=list)
    cis_controls: List[str] = field(default_factory=list)
    eu_cra: List[str] = field(default_factory=list)
    nis2: List[str] = field(default_factory=list)
    gdpr: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IEC 62443-3-3 SR -> multi-standard mapping
# ---------------------------------------------------------------------------

SR_MAPPINGS: Dict[str, StandardMapping] = {
    # FR1 - Identification and Authentication
    "SR 1.1": StandardMapping(
        iec62443_id="SR 1.1",
        nist_csf=["PR.AC-1", "PR.AC-7"],
        iso27001=["A.9.2.1", "A.9.2.2"],
        cis_controls=["CIS 5.1", "CIS 5.2", "CIS 6.3"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.2": StandardMapping(
        iec62443_id="SR 1.2",
        nist_csf=["PR.AC-1", "PR.AC-2"],
        iso27001=["A.9.2.1", "A.9.4.2"],
        cis_controls=["CIS 1.4", "CIS 5.2"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.3": StandardMapping(
        iec62443_id="SR 1.3",
        nist_csf=["PR.AC-1", "PR.AC-4"],
        iso27001=["A.9.2.1", "A.9.2.2", "A.9.2.5", "A.9.2.6"],
        cis_controls=["CIS 5.1", "CIS 5.3"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.4": StandardMapping(
        iec62443_id="SR 1.4",
        nist_csf=["PR.AC-1"],
        iso27001=["A.9.2.1"],
        cis_controls=["CIS 5.1"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.5": StandardMapping(
        iec62443_id="SR 1.5",
        nist_csf=["PR.AC-1", "PR.AC-7"],
        iso27001=["A.9.2.4", "A.9.3.1", "A.9.4.3"],
        cis_controls=["CIS 5.2"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(j)"],
        gdpr=[],
    ),
    "SR 1.6": StandardMapping(
        iec62443_id="SR 1.6",
        nist_csf=["PR.AC-1", "PR.AC-3"],
        iso27001=["A.9.1.2", "A.13.1.1"],
        cis_controls=["CIS 15.4", "CIS 15.5"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.7": StandardMapping(
        iec62443_id="SR 1.7",
        nist_csf=["PR.AC-7"],
        iso27001=["A.9.4.3"],
        cis_controls=["CIS 5.2"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(j)"],
        gdpr=[],
    ),
    "SR 1.8": StandardMapping(
        iec62443_id="SR 1.8",
        nist_csf=["PR.AC-7", "PR.DS-2"],
        iso27001=["A.10.1.2", "A.14.1.3"],
        cis_controls=["CIS 3.10"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(h)"],
        gdpr=[],
    ),
    "SR 1.9": StandardMapping(
        iec62443_id="SR 1.9",
        nist_csf=["PR.AC-7", "PR.DS-2"],
        iso27001=["A.10.1.1"],
        cis_controls=["CIS 3.10"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(h)"],
        gdpr=[],
    ),
    "SR 1.10": StandardMapping(
        iec62443_id="SR 1.10",
        nist_csf=["PR.AC-7"],
        iso27001=["A.9.4.2"],
        cis_controls=["CIS 5.2"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 1.11": StandardMapping(
        iec62443_id="SR 1.11",
        nist_csf=["PR.AC-7"],
        iso27001=["A.9.4.2"],
        cis_controls=["CIS 5.5"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 1.12": StandardMapping(
        iec62443_id="SR 1.12",
        nist_csf=["PR.AT-1"],
        iso27001=["A.9.4.2"],
        cis_controls=[],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 1.13": StandardMapping(
        iec62443_id="SR 1.13",
        nist_csf=["PR.AC-3", "PR.AC-5"],
        iso27001=["A.9.1.2", "A.13.1.1", "A.13.2.1"],
        cis_controls=["CIS 12.6"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=[],
    ),
    # FR2 - Use Control
    "SR 2.1": StandardMapping(
        iec62443_id="SR 2.1",
        nist_csf=["PR.AC-4"],
        iso27001=["A.9.1.1", "A.9.2.3", "A.9.4.1"],
        cis_controls=["CIS 6.1", "CIS 6.8"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=["Art. 32(1)(b)"],
    ),
    "SR 2.2": StandardMapping(
        iec62443_id="SR 2.2",
        nist_csf=["PR.AC-3"],
        iso27001=["A.13.1.1"],
        cis_controls=["CIS 15.4"],
        eu_cra=["Annex I, Part I(2)(d)"],
        nis2=["Art. 21(2)(i)"],
        gdpr=[],
    ),
    "SR 2.3": StandardMapping(
        iec62443_id="SR 2.3",
        nist_csf=["PR.AC-3"],
        iso27001=["A.6.2.1", "A.11.2.6"],
        cis_controls=["CIS 1.4"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.4": StandardMapping(
        iec62443_id="SR 2.4",
        nist_csf=["PR.PT-2"],
        iso27001=["A.12.5.1", "A.12.6.2"],
        cis_controls=["CIS 2.7"],
        eu_cra=["Annex I, Part I(2)(c)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.5": StandardMapping(
        iec62443_id="SR 2.5",
        nist_csf=["PR.AC-7"],
        iso27001=["A.11.2.8", "A.11.2.9"],
        cis_controls=["CIS 4.3"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.6": StandardMapping(
        iec62443_id="SR 2.6",
        nist_csf=["PR.AC-5"],
        iso27001=["A.9.4.2"],
        cis_controls=["CIS 4.3"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.7": StandardMapping(
        iec62443_id="SR 2.7",
        nist_csf=["PR.AC-5"],
        iso27001=["A.9.4.2"],
        cis_controls=["CIS 4.3"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.8": StandardMapping(
        iec62443_id="SR 2.8",
        nist_csf=["DE.AE-3", "PR.PT-1"],
        iso27001=["A.12.4.1", "A.12.4.3"],
        cis_controls=["CIS 8.2", "CIS 8.5"],
        eu_cra=["Annex I, Part I(2)(b)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=["Art. 5(2)"],
    ),
    "SR 2.9": StandardMapping(
        iec62443_id="SR 2.9",
        nist_csf=["PR.PT-1"],
        iso27001=["A.12.4.1"],
        cis_controls=["CIS 8.3"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.10": StandardMapping(
        iec62443_id="SR 2.10",
        nist_csf=["DE.AE-5"],
        iso27001=["A.12.4.1"],
        cis_controls=["CIS 8.2"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.11": StandardMapping(
        iec62443_id="SR 2.11",
        nist_csf=["PR.PT-1"],
        iso27001=["A.12.4.4"],
        cis_controls=["CIS 8.4"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 2.12": StandardMapping(
        iec62443_id="SR 2.12",
        nist_csf=["PR.PT-1"],
        iso27001=["A.18.1.3"],
        cis_controls=[],
        eu_cra=[],
        nis2=[],
        gdpr=["Art. 5(2)"],
    ),
    # FR3 - System Integrity
    "SR 3.1": StandardMapping(
        iec62443_id="SR 3.1",
        nist_csf=["PR.DS-2", "PR.DS-6"],
        iso27001=["A.13.2.1", "A.14.1.2", "A.14.1.3"],
        cis_controls=["CIS 3.10"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(h)"],
        gdpr=["Art. 32(1)(a)"],
    ),
    "SR 3.2": StandardMapping(
        iec62443_id="SR 3.2",
        nist_csf=["DE.CM-4", "PR.DS-6"],
        iso27001=["A.12.2.1"],
        cis_controls=["CIS 10.1", "CIS 10.2"],
        eu_cra=["Annex I, Part I(2)(c)"],
        nis2=["Art. 21(2)(d)"],
        gdpr=[],
    ),
    "SR 3.3": StandardMapping(
        iec62443_id="SR 3.3",
        nist_csf=["DE.DP-3"],
        iso27001=["A.14.2.8"],
        cis_controls=[],
        eu_cra=["Annex I, Part I(2)(f)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 3.4": StandardMapping(
        iec62443_id="SR 3.4",
        nist_csf=["PR.DS-6"],
        iso27001=["A.12.5.1", "A.14.2.4"],
        cis_controls=["CIS 2.3"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(d)"],
        gdpr=["Art. 32(1)(b)"],
    ),
    "SR 3.5": StandardMapping(
        iec62443_id="SR 3.5",
        nist_csf=["PR.DS-5"],
        iso27001=["A.14.2.5"],
        cis_controls=["CIS 16.2"],
        eu_cra=["Annex I, Part I(2)(c)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 3.6": StandardMapping(
        iec62443_id="SR 3.6",
        nist_csf=["PR.IP-9"],
        iso27001=["A.17.1.1"],
        cis_controls=[],
        eu_cra=["Annex I, Part I(2)(e)"],
        nis2=["Art. 21(2)(c)"],
        gdpr=[],
    ),
    "SR 3.7": StandardMapping(
        iec62443_id="SR 3.7",
        nist_csf=["PR.DS-5"],
        iso27001=["A.14.2.1"],
        cis_controls=["CIS 16.2"],
        eu_cra=["Annex I, Part I(2)(c)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 3.8": StandardMapping(
        iec62443_id="SR 3.8",
        nist_csf=["PR.AC-5"],
        iso27001=["A.14.1.2"],
        cis_controls=[],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 3.9": StandardMapping(
        iec62443_id="SR 3.9",
        nist_csf=["PR.PT-1"],
        iso27001=["A.12.4.2"],
        cis_controls=["CIS 8.2"],
        eu_cra=["Annex I, Part I(2)(b)"],
        nis2=[],
        gdpr=[],
    ),
    # FR4 - Data Confidentiality
    "SR 4.1": StandardMapping(
        iec62443_id="SR 4.1",
        nist_csf=["PR.DS-1", "PR.DS-2"],
        iso27001=["A.8.2.3", "A.10.1.1", "A.13.2.1"],
        cis_controls=["CIS 3.7", "CIS 3.10"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(h)"],
        gdpr=["Art. 32(1)(a)"],
    ),
    "SR 4.2": StandardMapping(
        iec62443_id="SR 4.2",
        nist_csf=["PR.DS-3"],
        iso27001=["A.8.3.2", "A.11.2.7"],
        cis_controls=["CIS 3.1"],
        eu_cra=[],
        nis2=[],
        gdpr=["Art. 17"],
    ),
    "SR 4.3": StandardMapping(
        iec62443_id="SR 4.3",
        nist_csf=["PR.DS-1", "PR.DS-2"],
        iso27001=["A.10.1.1", "A.10.1.2", "A.14.1.2"],
        cis_controls=["CIS 3.10", "CIS 3.11"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(h)"],
        gdpr=["Art. 32(1)(a)"],
    ),
    # FR5 - Restricted Data Flow
    "SR 5.1": StandardMapping(
        iec62443_id="SR 5.1",
        nist_csf=["PR.AC-5"],
        iso27001=["A.13.1.1", "A.13.1.3"],
        cis_controls=["CIS 12.2", "CIS 12.8"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=[],
    ),
    "SR 5.2": StandardMapping(
        iec62443_id="SR 5.2",
        nist_csf=["PR.AC-5", "DE.CM-1"],
        iso27001=["A.13.1.1", "A.13.1.2"],
        cis_controls=["CIS 12.2", "CIS 12.4"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=[],
    ),
    "SR 5.3": StandardMapping(
        iec62443_id="SR 5.3",
        nist_csf=["PR.AC-5"],
        iso27001=["A.13.1.1"],
        cis_controls=["CIS 12.2"],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 5.4": StandardMapping(
        iec62443_id="SR 5.4",
        nist_csf=["PR.PT-3"],
        iso27001=["A.14.2.1"],
        cis_controls=["CIS 16.8"],
        eu_cra=["Annex I, Part I(2)(c)"],
        nis2=[],
        gdpr=[],
    ),
    # FR6 - Timely Response to Events
    "SR 6.1": StandardMapping(
        iec62443_id="SR 6.1",
        nist_csf=["PR.PT-1", "DE.AE-3"],
        iso27001=["A.12.4.1", "A.12.4.3"],
        cis_controls=["CIS 8.1", "CIS 8.2"],
        eu_cra=["Annex I, Part I(2)(b)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=[],
    ),
    "SR 6.2": StandardMapping(
        iec62443_id="SR 6.2",
        nist_csf=["DE.CM-1", "DE.CM-7", "DE.DP-3"],
        iso27001=["A.12.4.1", "A.16.1.2"],
        cis_controls=["CIS 8.2", "CIS 8.11"],
        eu_cra=["Annex I, Part I(2)(b)"],
        nis2=["Art. 21(2)(b)"],
        gdpr=[],
    ),
    # FR7 - Resource Availability
    "SR 7.1": StandardMapping(
        iec62443_id="SR 7.1",
        nist_csf=["PR.PT-5", "DE.CM-1"],
        iso27001=["A.17.1.1", "A.17.2.1"],
        cis_controls=["CIS 12.2"],
        eu_cra=["Annex I, Part I(2)(e)"],
        nis2=["Art. 21(2)(c)"],
        gdpr=["Art. 32(1)(b)"],
    ),
    "SR 7.2": StandardMapping(
        iec62443_id="SR 7.2",
        nist_csf=["PR.DS-4"],
        iso27001=["A.12.1.3"],
        cis_controls=[],
        eu_cra=["Annex I, Part I(2)(e)"],
        nis2=[],
        gdpr=[],
    ),
    "SR 7.3": StandardMapping(
        iec62443_id="SR 7.3",
        nist_csf=["PR.IP-4"],
        iso27001=["A.12.3.1"],
        cis_controls=["CIS 11.2", "CIS 11.4"],
        eu_cra=["Annex I, Part I(2)(e)"],
        nis2=["Art. 21(2)(c)"],
        gdpr=["Art. 32(1)(c)"],
    ),
    "SR 7.4": StandardMapping(
        iec62443_id="SR 7.4",
        nist_csf=["RC.RP-1", "PR.IP-9"],
        iso27001=["A.17.1.1", "A.17.1.2"],
        cis_controls=["CIS 11.1"],
        eu_cra=["Annex I, Part I(2)(e)"],
        nis2=["Art. 21(2)(c)"],
        gdpr=["Art. 32(1)(c)"],
    ),
    "SR 7.5": StandardMapping(
        iec62443_id="SR 7.5",
        nist_csf=["PR.IP-5"],
        iso27001=["A.11.2.2"],
        cis_controls=[],
        eu_cra=[],
        nis2=[],
        gdpr=[],
    ),
    "SR 7.6": StandardMapping(
        iec62443_id="SR 7.6",
        nist_csf=["PR.IP-1"],
        iso27001=["A.12.1.1", "A.14.2.2"],
        cis_controls=["CIS 4.1"],
        eu_cra=["Annex I, Part I(2)(f)"],
        nis2=["Art. 21(2)(e)"],
        gdpr=[],
    ),
    "SR 7.7": StandardMapping(
        iec62443_id="SR 7.7",
        nist_csf=["PR.PT-3"],
        iso27001=["A.12.5.1", "A.12.6.2"],
        cis_controls=["CIS 4.8", "CIS 7.7"],
        eu_cra=["Annex I, Part I(2)(a)"],
        nis2=["Art. 21(2)(e)"],
        gdpr=[],
    ),
    "SR 7.8": StandardMapping(
        iec62443_id="SR 7.8",
        nist_csf=["ID.AM-1", "ID.AM-2"],
        iso27001=["A.8.1.1", "A.8.1.2"],
        cis_controls=["CIS 1.1", "CIS 2.1"],
        eu_cra=["Annex I, Part I(2)(f)"],
        nis2=["Art. 21(2)(e)"],
        gdpr=[],
    ),
}


def get_mapping(sr_id: str) -> Optional[StandardMapping]:
    """Get the cross-standard mapping for an IEC 62443 SR/CR ID."""
    return SR_MAPPINGS.get(sr_id)


def get_all_mappings() -> Dict[str, StandardMapping]:
    """Return the complete mapping dictionary."""
    return SR_MAPPINGS


STANDARD_NAMES = {
    "nist_csf": "NIST Cybersecurity Framework",
    "iso27001": "ISO/IEC 27001:2022",
    "cis_controls": "CIS Controls v8",
    "eu_cra": "EU Cyber Resilience Act",
    "nis2": "NIS2 Directive",
    "gdpr": "GDPR",
}


def get_mapped_standards_for_sr(sr_id: str) -> Dict[str, List[str]]:
    """Return a dict of standard_name -> [control_ids] for a given SR.

    Returns an empty dict if no mapping exists.
    """
    mapping = get_mapping(sr_id)
    if not mapping:
        return {}
    result = {}
    for field_name in ("nist_csf", "iso27001", "cis_controls", "eu_cra", "nis2", "gdpr"):
        controls = getattr(mapping, field_name, [])
        if controls:
            result[STANDARD_NAMES[field_name]] = controls
    return result
