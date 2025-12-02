"""IEC 62443-4-2 component-level requirements (CRs) for device-level assessments.

Defines Component Requirements mapped to the same seven Foundational
Requirements as IEC 62443-3-3, but focused on individual component
capabilities rather than system-level requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ComponentRequirement:
    """A single Component Requirement within a Foundational Requirement."""

    id: str
    name: str
    description: str
    sl_capability: int  # minimum SL where this CR applies (1-4)
    component_type: str = "all"  # all, embedded, host, network, software


@dataclass
class FoundationalRequirement42:
    """One of the seven IEC 62443-4-2 Foundational Requirements for components."""

    id: str
    name: str
    abbreviation: str
    description: str
    component_requirements: List[ComponentRequirement] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IEC 62443-4-2 Component Requirements
# ---------------------------------------------------------------------------

COMPONENT_REQUIREMENTS: List[FoundationalRequirement42] = [
    # -----------------------------------------------------------------------
    # FR 1 -- Identification and Authentication Control (IAC)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR1",
        name="Identification and Authentication Control",
        abbreviation="IAC",
        description=(
            "Component-level identification and authentication capabilities "
            "for users, processes, and devices."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 1.1",
                name="Human user identification and authentication",
                description=(
                    "The component shall provide the capability to identify and "
                    "authenticate all human users. Multi-factor authentication "
                    "shall be supported at higher SLs."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.2",
                name="Software process and device identification and authentication",
                description=(
                    "The component shall provide the capability to identify and "
                    "authenticate all software processes and devices that attempt "
                    "to connect to or through the component."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.3",
                name="Account management",
                description=(
                    "The component shall support account management including "
                    "creation, modification, disabling, and removal of accounts."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.4",
                name="Identifier management",
                description=(
                    "The component shall support unique identifier management "
                    "by user, group, role, or interface."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.5",
                name="Authenticator management",
                description=(
                    "The component shall manage authenticators including initial "
                    "distribution, credential lifecycle, and revocation. Password "
                    "complexity enforcement shall be configurable."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.6",
                name="Wireless access management",
                description=(
                    "The component shall identify and authenticate all wireless "
                    "connections using industry-standard protocols."
                ),
                sl_capability=1,
                component_type="network",
            ),
            ComponentRequirement(
                id="CR 1.7",
                name="Strength of password-based authentication",
                description=(
                    "The component shall enforce configurable minimum password "
                    "strength including length, complexity, and aging requirements."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.8",
                name="Public key infrastructure certificates",
                description=(
                    "The component shall support PKI certificate-based "
                    "authentication with certificate chain validation and "
                    "revocation checking."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 1.9",
                name="Strength of public key authentication",
                description=(
                    "The component shall use public key lengths and algorithms "
                    "meeting recognized industry standards (e.g., RSA 2048+, "
                    "ECC P-256+)."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 1.10",
                name="Authenticator feedback",
                description=(
                    "The component shall obscure authentication feedback to "
                    "prevent credential exposure during the login process."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.11",
                name="Unsuccessful login attempts",
                description=(
                    "The component shall enforce a configurable lockout after "
                    "consecutive failed authentication attempts."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.12",
                name="System use notification",
                description=(
                    "The component shall display a configurable security use "
                    "notification banner before granting access."
                ),
                sl_capability=1,
                component_type="host",
            ),
            ComponentRequirement(
                id="CR 1.13",
                name="Access via untrusted networks",
                description=(
                    "The component shall provide mechanisms to monitor and "
                    "restrict access originating from untrusted networks."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 1.14",
                name="Strength of symmetric key authentication",
                description=(
                    "The component shall use symmetric key lengths and algorithms "
                    "meeting recognized industry standards (e.g., AES-128+)."
                ),
                sl_capability=2,
                component_type="embedded",
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 2 -- Use Control (UC)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR2",
        name="Use Control",
        abbreviation="UC",
        description=(
            "Component-level authorization enforcement and privilege "
            "management capabilities."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 2.1",
                name="Authorization enforcement",
                description=(
                    "The component shall enforce role-based or attribute-based "
                    "authorization on all interfaces."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.2",
                name="Wireless use control",
                description=(
                    "The component shall enforce authorization, monitoring, and "
                    "usage restrictions for wireless connectivity."
                ),
                sl_capability=2,
                component_type="network",
            ),
            ComponentRequirement(
                id="CR 2.3",
                name="Use control for portable and mobile devices",
                description=(
                    "The component shall enforce security policies for portable "
                    "and mobile device connections."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.4",
                name="Mobile code",
                description=(
                    "The component shall restrict and control execution of "
                    "mobile code, preventing unauthorized code execution."
                ),
                sl_capability=2,
                component_type="host",
            ),
            ComponentRequirement(
                id="CR 2.5",
                name="Session lock",
                description=(
                    "The component shall lock sessions after a configurable "
                    "inactivity period, requiring re-authentication to resume."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.6",
                name="Remote session termination",
                description=(
                    "The component shall automatically terminate remote sessions "
                    "after a configurable inactivity period."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 2.7",
                name="Concurrent session control",
                description=(
                    "The component shall limit concurrent sessions per user to "
                    "a configurable maximum."
                ),
                sl_capability=3,
            ),
            ComponentRequirement(
                id="CR 2.8",
                name="Auditable events",
                description=(
                    "The component shall generate audit records for security-"
                    "relevant events including authentication, authorization "
                    "decisions, and configuration changes."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.9",
                name="Audit storage capacity",
                description=(
                    "The component shall provide sufficient local audit record "
                    "storage or support external log forwarding (e.g., syslog)."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.10",
                name="Response to audit processing failures",
                description=(
                    "The component shall alert on audit processing failures and "
                    "prevent loss of critical audit records."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.11",
                name="Timestamps",
                description=(
                    "The component shall include accurate timestamps in audit "
                    "records, synchronized via NTP or equivalent."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 2.12",
                name="Non-repudiation",
                description=(
                    "The component shall provide cryptographic non-repudiation "
                    "for critical actions (e.g., signed audit logs)."
                ),
                sl_capability=3,
            ),
            ComponentRequirement(
                id="CR 2.13",
                name="Use of physical diagnostic and test interfaces",
                description=(
                    "The component shall restrict access to physical diagnostic "
                    "and test interfaces (JTAG, serial debug) by default."
                ),
                sl_capability=1,
                component_type="embedded",
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 3 -- System Integrity (SI)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR3",
        name="System Integrity",
        abbreviation="SI",
        description=(
            "Component-level integrity protection for firmware, software, "
            "and communications."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 3.1",
                name="Communication integrity",
                description=(
                    "The component shall protect integrity of all transmitted "
                    "data using cryptographic mechanisms (e.g., HMAC, TLS)."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.2",
                name="Malicious code protection",
                description=(
                    "The component shall employ mechanisms to detect and prevent "
                    "execution of malicious code, including whitelisting on "
                    "embedded devices."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.3",
                name="Security functionality verification",
                description=(
                    "The component shall support self-test of security functions "
                    "at startup and periodically during operation."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.4",
                name="Software and information integrity",
                description=(
                    "The component shall verify integrity of firmware and "
                    "software using cryptographic signatures before execution."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.5",
                name="Input validation",
                description=(
                    "The component shall validate all inputs from external "
                    "sources and industrial process interfaces."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.6",
                name="Deterministic output",
                description=(
                    "The component shall set outputs to a safe, predetermined "
                    "state when a security compromise is detected."
                ),
                sl_capability=1,
                component_type="embedded",
            ),
            ComponentRequirement(
                id="CR 3.7",
                name="Error handling",
                description=(
                    "The component shall handle errors without exposing "
                    "information useful to an attacker."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 3.8",
                name="Session integrity",
                description=(
                    "The component shall protect session integrity, preventing "
                    "session hijacking and replay attacks."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 3.9",
                name="Protection of audit information",
                description=(
                    "The component shall protect stored audit information from "
                    "unauthorized modification or deletion."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 3.10",
                name="Support of updates",
                description=(
                    "The component shall support secure, authenticated firmware "
                    "and software updates with rollback capability."
                ),
                sl_capability=1,
                component_type="embedded",
            ),
            ComponentRequirement(
                id="CR 3.11",
                name="Physical tamper resistance and detection",
                description=(
                    "The component shall provide physical tamper detection or "
                    "resistance mechanisms appropriate to the deployment "
                    "environment."
                ),
                sl_capability=3,
                component_type="embedded",
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 4 -- Data Confidentiality (DC)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR4",
        name="Data Confidentiality",
        abbreviation="DC",
        description=(
            "Component-level data confidentiality for stored and transmitted "
            "information."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 4.1",
                name="Information confidentiality",
                description=(
                    "The component shall protect confidentiality of sensitive "
                    "data at rest and in transit using encryption."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 4.2",
                name="Information persistence",
                description=(
                    "The component shall securely purge sensitive data from "
                    "volatile and non-volatile memory when no longer needed."
                ),
                sl_capability=2,
            ),
            ComponentRequirement(
                id="CR 4.3",
                name="Use of cryptography",
                description=(
                    "The component shall use NIST/BSI-approved cryptographic "
                    "algorithms and key management practices."
                ),
                sl_capability=2,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 5 -- Restricted Data Flow (RDF)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR5",
        name="Restricted Data Flow",
        abbreviation="RDF",
        description=(
            "Component-level network segmentation and data flow control."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 5.1",
                name="Network segmentation",
                description=(
                    "The component shall support logical network segmentation "
                    "via VLANs, firewall rules, or equivalent mechanisms."
                ),
                sl_capability=1,
                component_type="network",
            ),
            ComponentRequirement(
                id="CR 5.2",
                name="Zone boundary protection",
                description=(
                    "The component shall enforce deny-by-default policies at "
                    "zone boundaries with deep packet inspection for industrial "
                    "protocols."
                ),
                sl_capability=1,
                component_type="network",
            ),
            ComponentRequirement(
                id="CR 5.3",
                name="General purpose person-to-person communication restrictions",
                description=(
                    "The component shall block general-purpose messaging "
                    "protocols on control network interfaces."
                ),
                sl_capability=2,
                component_type="network",
            ),
            ComponentRequirement(
                id="CR 5.4",
                name="Application partitioning",
                description=(
                    "The component shall support process isolation or sandboxing "
                    "for security-critical applications."
                ),
                sl_capability=2,
                component_type="host",
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 6 -- Timely Response to Events (TRE)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR6",
        name="Timely Response to Events",
        abbreviation="TRE",
        description=(
            "Component-level event detection, logging, and notification."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 6.1",
                name="Audit log accessibility",
                description=(
                    "The component shall provide read-only access to audit logs "
                    "via standard interfaces (syslog, SNMP, REST API)."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 6.2",
                name="Continuous monitoring",
                description=(
                    "The component shall support real-time security event "
                    "reporting to external SIEM/monitoring systems."
                ),
                sl_capability=3,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 7 -- Resource Availability (RA)
    # -----------------------------------------------------------------------
    FoundationalRequirement42(
        id="FR7",
        name="Resource Availability",
        abbreviation="RA",
        description=(
            "Component-level availability, resilience, and recovery capabilities."
        ),
        component_requirements=[
            ComponentRequirement(
                id="CR 7.1",
                name="Denial of service protection",
                description=(
                    "The component shall maintain essential functions during "
                    "network-based denial-of-service conditions via rate limiting, "
                    "connection limits, and traffic prioritization."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.2",
                name="Resource management",
                description=(
                    "The component shall prevent security functions from "
                    "exhausting critical system resources (CPU, memory, storage)."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.3",
                name="Control system backup",
                description=(
                    "The component shall support automated configuration backup "
                    "and verified restore within defined recovery time objectives."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.4",
                name="Control system recovery and reconstitution",
                description=(
                    "The component shall support recovery to a known secure "
                    "state including factory reset capability."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.5",
                name="Emergency power",
                description=(
                    "The component shall maintain security state during power "
                    "transitions and support orderly shutdown on power loss."
                ),
                sl_capability=1,
                component_type="embedded",
            ),
            ComponentRequirement(
                id="CR 7.6",
                name="Network and security configuration settings",
                description=(
                    "The component shall support hardened default configurations "
                    "and provide configuration verification mechanisms."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.7",
                name="Least functionality",
                description=(
                    "The component shall disable unnecessary services, ports, "
                    "and protocols by default. Configuration changes shall be "
                    "audit-logged."
                ),
                sl_capability=1,
            ),
            ComponentRequirement(
                id="CR 7.8",
                name="Control system component inventory",
                description=(
                    "The component shall report its hardware/firmware/software "
                    "inventory via standard asset discovery protocols."
                ),
                sl_capability=2,
            ),
        ],
    ),
]


def get_all_component_requirements() -> List[FoundationalRequirement42]:
    """Return all IEC 62443-4-2 foundational requirements with CRs."""
    return COMPONENT_REQUIREMENTS


def get_cr_by_fr(fr_id: str) -> FoundationalRequirement42 | None:
    """Look up component requirements by FR ID."""
    for fr in COMPONENT_REQUIREMENTS:
        if fr.id == fr_id:
            return fr
    return None


def total_cr_count() -> int:
    """Return the total number of component requirements across all FRs."""
    return sum(len(fr.component_requirements) for fr in COMPONENT_REQUIREMENTS)
