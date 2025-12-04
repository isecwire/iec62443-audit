"""IEC 62443-3-3 foundational requirements and system requirements data.

This module defines the seven Foundational Requirements (FRs) and their
associated System Requirements (SRs) as specified in IEC 62443-3-3.
Each SR includes a description and the security level (SL) at which it
becomes applicable (SL1 through SL4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SystemRequirement:
    """A single System Requirement within a Foundational Requirement."""

    id: str
    name: str
    description: str
    sl_capability: int  # minimum SL where this SR applies (1-4)


@dataclass
class FoundationalRequirement:
    """One of the seven IEC 62443-3-3 Foundational Requirements."""

    id: str
    name: str
    abbreviation: str
    description: str
    system_requirements: List[SystemRequirement] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IEC 62443-3-3 Foundational Requirements with System Requirements
# ---------------------------------------------------------------------------

FOUNDATIONAL_REQUIREMENTS: List[FoundationalRequirement] = [
    # -----------------------------------------------------------------------
    # FR 1 -- Identification and Authentication Control (IAC)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR1",
        name="Identification and Authentication Control",
        abbreviation="IAC",
        description=(
            "Identify and authenticate all users (humans, software processes, "
            "and devices) before allowing access to the control system."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 1.1",
                name="Human user identification and authentication",
                description=(
                    "The control system shall provide the capability to identify "
                    "and authenticate all human users. This capability shall "
                    "enforce such identification and authentication on all "
                    "interfaces that provide human user access to the control "
                    "system."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.2",
                name="Software process and device identification and authentication",
                description=(
                    "The control system shall provide the capability to identify "
                    "and authenticate all software processes and devices. This "
                    "applies to all connections whether local, remote, or via "
                    "wireless networks."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.3",
                name="Account management",
                description=(
                    "The control system shall provide the capability to support "
                    "the management of all accounts by authorized users, including "
                    "adding, activating, modifying, disabling, and removing "
                    "accounts."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.4",
                name="Identifier management",
                description=(
                    "The control system shall provide the capability to support "
                    "the management of identifiers by user, group, role, or "
                    "control system interface."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.5",
                name="Authenticator management",
                description=(
                    "The control system shall provide the capability to manage "
                    "authenticators including initial distribution, lost or "
                    "compromised credentials, and revocation of credentials. "
                    "Passwords shall meet minimum complexity requirements."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.6",
                name="Wireless access management",
                description=(
                    "The control system shall provide the capability to identify "
                    "and authenticate all users (humans, software processes, and "
                    "devices) engaged in wireless communication."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.7",
                name="Strength of password-based authentication",
                description=(
                    "The control system shall provide the capability to enforce "
                    "configurable password strength based on minimum length, "
                    "variety of character types, and other attributes as defined "
                    "by the organization."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.8",
                name="Public key infrastructure certificates",
                description=(
                    "The control system shall provide the capability to use PKI "
                    "certificates for authentication of users and devices, "
                    "including validation of certificate chains and revocation "
                    "status."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 1.9",
                name="Strength of public key authentication",
                description=(
                    "The control system shall provide the capability to ensure "
                    "that public key-based authentication uses key lengths and "
                    "algorithms that meet recognized industry standards."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 1.10",
                name="Authenticator feedback",
                description=(
                    "The control system shall provide the capability to obscure "
                    "feedback of authentication information during the "
                    "authentication process."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.11",
                name="Unsuccessful login attempts",
                description=(
                    "The control system shall provide the capability to enforce "
                    "a limit of consecutive invalid access attempts by any user "
                    "during a configurable time period, and deny access for a "
                    "specified duration or until unlocked by an administrator."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.12",
                name="System use notification",
                description=(
                    "The control system shall provide the capability to display "
                    "a system use notification message before authenticating, "
                    "informing users of applicable security policies."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 1.13",
                name="Access via untrusted networks",
                description=(
                    "The control system shall provide the capability to monitor "
                    "and control all methods of access to the control system via "
                    "untrusted networks."
                ),
                sl_capability=1,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 2 -- Use Control (UC)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR2",
        name="Use Control",
        abbreviation="UC",
        description=(
            "Enforce the assigned privileges of an authenticated user to "
            "perform the requested action on the control system and monitor "
            "the use of those privileges."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 2.1",
                name="Authorization enforcement",
                description=(
                    "The control system shall provide the capability to enforce "
                    "authorizations assigned to all human users for controlling "
                    "use of the control system, on all interfaces."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.2",
                name="Wireless use control",
                description=(
                    "The control system shall provide the capability to authorize, "
                    "monitor, and enforce usage restrictions for wireless "
                    "connectivity to the control system."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 2.3",
                name="Use control for portable and mobile devices",
                description=(
                    "The control system shall provide the capability to enforce "
                    "usage restrictions and security policies for portable and "
                    "mobile devices connected to the control system."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.4",
                name="Mobile code",
                description=(
                    "The control system shall provide the capability to enforce "
                    "usage restrictions for mobile code technologies, including "
                    "prevention of execution of unauthorized mobile code."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 2.5",
                name="Session lock",
                description=(
                    "The control system shall provide the capability to prevent "
                    "further access by initiating a session lock after a "
                    "configurable time period of inactivity, retainable until "
                    "re-authenticated."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.6",
                name="Remote session termination",
                description=(
                    "The control system shall provide the capability to terminate "
                    "a remote session either automatically after a configurable "
                    "time period of inactivity or manually by the user."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 2.7",
                name="Concurrent session control",
                description=(
                    "The control system shall provide the capability to limit "
                    "the number of concurrent sessions per user interface to a "
                    "configurable number."
                ),
                sl_capability=3,
            ),
            SystemRequirement(
                id="SR 2.8",
                name="Auditable events",
                description=(
                    "The control system shall provide the capability to generate "
                    "audit records for auditable events including access control "
                    "decisions and security-related configuration changes."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.9",
                name="Audit storage capacity",
                description=(
                    "The control system shall provide the capability to allocate "
                    "sufficient audit record storage capacity according to "
                    "commonly recognized recommendations for log management."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.10",
                name="Response to audit processing failures",
                description=(
                    "The control system shall provide the capability to alert "
                    "personnel and prevent the loss of essential audit records "
                    "in the event of an audit processing failure."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.11",
                name="Timestamps",
                description=(
                    "The control system shall provide the capability to use "
                    "timestamps from a reliable, internal or external time "
                    "source in audit records."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 2.12",
                name="Non-repudiation",
                description=(
                    "The control system shall provide the capability to ensure "
                    "non-repudiation for all users, preventing denial of having "
                    "performed a specific action."
                ),
                sl_capability=3,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 3 -- System Integrity (SI)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR3",
        name="System Integrity",
        abbreviation="SI",
        description=(
            "Ensure the integrity of the control system to prevent "
            "unauthorized manipulation."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 3.1",
                name="Communication integrity",
                description=(
                    "The control system shall provide the capability to protect "
                    "the integrity of transmitted information, detecting "
                    "unauthorized changes to data during communication."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.2",
                name="Malicious code protection",
                description=(
                    "The control system shall provide the capability to employ "
                    "protection mechanisms to prevent, detect, report, and "
                    "mitigate the effects of malicious code or unauthorized "
                    "software."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.3",
                name="Security functionality verification",
                description=(
                    "The control system shall provide the capability to support "
                    "verification of the intended operation of security "
                    "functions and report when anomalies are discovered."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.4",
                name="Software and information integrity",
                description=(
                    "The control system shall provide the capability to detect, "
                    "record, report, and protect against unauthorized changes to "
                    "software and information at rest."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.5",
                name="Input validation",
                description=(
                    "The control system shall validate the syntax and content "
                    "of any input which is used as an industrial process control "
                    "input or input that directly affects the action of the "
                    "control system."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.6",
                name="Deterministic output",
                description=(
                    "The control system shall provide the capability to set "
                    "outputs to a predetermined state if normal operation cannot "
                    "be maintained as a result of an attack."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 3.7",
                name="Error handling",
                description=(
                    "The control system shall provide the capability to perform "
                    "error handling so that error conditions do not provide "
                    "information that could be exploited by adversaries."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 3.8",
                name="Session integrity",
                description=(
                    "The control system shall provide the capability to protect "
                    "the integrity of sessions, rejecting invalid session IDs "
                    "and preventing session hijacking."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 3.9",
                name="Protection of audit information",
                description=(
                    "The control system shall protect audit information and "
                    "audit tools from unauthorized access, modification, and "
                    "deletion."
                ),
                sl_capability=1,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 4 -- Data Confidentiality (DC)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR4",
        name="Data Confidentiality",
        abbreviation="DC",
        description=(
            "Ensure the confidentiality of information on communication "
            "channels and in data repositories to prevent unauthorized "
            "disclosure."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 4.1",
                name="Information confidentiality",
                description=(
                    "The control system shall provide the capability to protect "
                    "the confidentiality of information for which explicit read "
                    "authorization is supported, whether at rest or in transit."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 4.2",
                name="Information persistence",
                description=(
                    "The control system shall provide the capability to purge "
                    "all information from resources associated with a connection "
                    "when the connection is terminated, preventing exposure of "
                    "residual data."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 4.3",
                name="Use of cryptography",
                description=(
                    "The control system shall use cryptographic mechanisms "
                    "recognized by accepted industry practices and "
                    "recommendations to protect the confidentiality of "
                    "information both at rest and in transit."
                ),
                sl_capability=2,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 5 -- Restricted Data Flow (RDF)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR5",
        name="Restricted Data Flow",
        abbreviation="RDF",
        description=(
            "Segment the control system via zones and conduits to limit the "
            "unnecessary flow of data."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 5.1",
                name="Network segmentation",
                description=(
                    "The control system shall provide the capability to logically "
                    "and physically segment control system networks from "
                    "non-control system networks and to segment critical control "
                    "system networks from other control system networks."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 5.2",
                name="Zone boundary protection",
                description=(
                    "The control system shall provide the capability to monitor "
                    "and control communications at zone boundaries, employing "
                    "deny-by-default and allow-by-exception policies."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 5.3",
                name="General purpose person-to-person communication restrictions",
                description=(
                    "The control system shall provide the capability to prevent "
                    "general purpose person-to-person messaging on control "
                    "system networks to reduce the attack surface."
                ),
                sl_capability=2,
            ),
            SystemRequirement(
                id="SR 5.4",
                name="Application partitioning",
                description=(
                    "The control system shall provide the capability to support "
                    "application partitioning, with security-critical "
                    "applications residing in separate execution domains."
                ),
                sl_capability=2,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 6 -- Timely Response to Events (TRE)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR6",
        name="Timely Response to Events",
        abbreviation="TRE",
        description=(
            "Respond to security violations by notifying the appropriate "
            "authority, reporting needed evidence of the violation, and "
            "taking timely corrective action."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 6.1",
                name="Audit log accessibility",
                description=(
                    "The control system shall provide the capability to make "
                    "audit logs accessible on a read-only basis to authorized "
                    "users for review and analysis."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 6.2",
                name="Continuous monitoring",
                description=(
                    "The control system shall provide the capability to "
                    "continuously monitor all security mechanisms to detect, "
                    "characterize, and report security breaches in a timely "
                    "manner."
                ),
                sl_capability=3,
            ),
        ],
    ),
    # -----------------------------------------------------------------------
    # FR 7 -- Resource Availability (RA)
    # -----------------------------------------------------------------------
    FoundationalRequirement(
        id="FR7",
        name="Resource Availability",
        abbreviation="RA",
        description=(
            "Ensure the availability of the control system against the "
            "degradation or denial of essential services."
        ),
        system_requirements=[
            SystemRequirement(
                id="SR 7.1",
                name="Denial of service protection",
                description=(
                    "The control system shall provide the capability to operate "
                    "in a degraded mode during a denial-of-service event, "
                    "maintaining essential functions while under attack."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.2",
                name="Resource management",
                description=(
                    "The control system shall provide the capability to limit "
                    "the use of resources by security functions to prevent "
                    "resource exhaustion of critical system resources."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.3",
                name="Control system backup",
                description=(
                    "The control system shall provide the capability to perform "
                    "and recover from backups of the control system within a "
                    "defined recovery time acceptable to the asset owner."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.4",
                name="Control system recovery and reconstitution",
                description=(
                    "The control system shall provide the capability to recover "
                    "and reconstitute to a known secure state after a disruption "
                    "or failure."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.5",
                name="Emergency power",
                description=(
                    "The control system shall provide the capability to switch "
                    "to and from an emergency power supply without affecting "
                    "the existing security state or a transition to a known "
                    "secure state."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.6",
                name="Network and security configuration settings",
                description=(
                    "The control system shall provide the capability to "
                    "configure and verify network and security settings using "
                    "a documented, minimal-footprint configuration as recommended "
                    "by trusted guides."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.7",
                name="Least functionality",
                description=(
                    "The control system shall provide the capability to "
                    "specifically restrict the use of unnecessary functions, "
                    "ports, protocols, and services."
                ),
                sl_capability=1,
            ),
            SystemRequirement(
                id="SR 7.8",
                name="Control system component inventory",
                description=(
                    "The control system shall provide the capability to report "
                    "its current list of installed components and their "
                    "associated properties."
                ),
                sl_capability=2,
            ),
        ],
    ),
]


def get_all_requirements() -> List[FoundationalRequirement]:
    """Return all foundational requirements."""
    return FOUNDATIONAL_REQUIREMENTS


def get_fr_by_id(fr_id: str) -> FoundationalRequirement | None:
    """Look up a foundational requirement by its ID (e.g. 'FR1')."""
    for fr in FOUNDATIONAL_REQUIREMENTS:
        if fr.id == fr_id:
            return fr
    return None


def total_sr_count() -> int:
    """Return the total number of system requirements across all FRs."""
    return sum(len(fr.system_requirements) for fr in FOUNDATIONAL_REQUIREMENTS)
