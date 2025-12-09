"""Action plan generator for IEC 62443 gap remediation.

For each identified gap, generates recommended actions with effort
estimates, priority levels, and timeline planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from iec62443_audit.scoring import AssessmentResult, SRResult


class Effort:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @staticmethod
    def from_gap(gap: int, sr_id: str) -> str:
        """Estimate effort based on gap magnitude and SR type."""
        if gap <= 0:
            return Effort.LOW
        if gap == 1:
            return Effort.LOW if sr_id.startswith("SR 6") or sr_id.startswith("SR 2.1") else Effort.MEDIUM
        if gap == 2:
            return Effort.MEDIUM
        return Effort.HIGH

    @staticmethod
    def days(effort: str) -> int:
        """Estimated working days per effort level."""
        return {"Low": 5, "Medium": 15, "High": 30}.get(effort, 15)


class Priority:
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    @staticmethod
    def from_gap_and_weight(gap: int, business_impact: float = 1.0) -> str:
        """Derive priority from gap size and business impact weight."""
        score = gap * business_impact
        if score >= 3.0:
            return Priority.CRITICAL
        if score >= 2.0:
            return Priority.HIGH
        if score >= 1.0:
            return Priority.MEDIUM
        return Priority.LOW

    @staticmethod
    def sort_key(priority: str) -> int:
        return {
            "Critical": 0,
            "High": 1,
            "Medium": 2,
            "Low": 3,
        }.get(priority, 99)


# ---------------------------------------------------------------------------
# Recommended actions per SR category
# ---------------------------------------------------------------------------

_SR_ACTIONS: Dict[str, str] = {
    "SR 1.1": "Implement centralized identity management (e.g., Active Directory integration). Deploy multi-factor authentication for all human access points.",
    "SR 1.2": "Deploy device certificates and mutual TLS for machine-to-machine communication. Implement service accounts with unique credentials.",
    "SR 1.3": "Establish formal account lifecycle management process. Implement automated provisioning/deprovisioning tied to HR systems.",
    "SR 1.4": "Implement unique user IDs mapped to roles. Eliminate shared accounts. Deploy group-based access with named individual tracking.",
    "SR 1.5": "Deploy enterprise password manager. Implement credential rotation policies. Set up automated expired credential detection.",
    "SR 1.6": "Implement WPA3-Enterprise with RADIUS. Deploy wireless IDS. Establish wireless access policy with periodic audits.",
    "SR 1.7": "Configure minimum 12-character passwords with complexity. Deploy password strength meters. Implement password history checking.",
    "SR 1.8": "Deploy internal PKI infrastructure. Configure certificate-based authentication for critical systems. Implement OCSP/CRL checking.",
    "SR 1.9": "Upgrade to RSA-2048+ or ECC P-256+ keys. Disable weak ciphers (3DES, RC4). Configure TLS 1.2+ only.",
    "SR 1.10": "Configure all login interfaces to mask password input. Remove any debugging interfaces that echo credentials.",
    "SR 1.11": "Configure account lockout after 5 failed attempts. Implement progressive delays. Set up failed login alerting.",
    "SR 1.12": "Deploy login banners on all system interfaces with approved security notice text.",
    "SR 1.13": "Implement VPN with MFA for remote access. Deploy jump servers. Monitor and log all external connections.",
    "SR 2.1": "Implement role-based access control (RBAC). Define operator, engineer, and administrator roles with least-privilege mapping.",
    "SR 2.2": "Deploy wireless access control with 802.1X. Implement wireless monitoring and rogue AP detection.",
    "SR 2.3": "Create BYOD security policy. Deploy MDM solution. Implement network access control for portable devices.",
    "SR 2.4": "Disable unnecessary browser plugins and scripting engines. Implement application whitelisting for mobile code.",
    "SR 2.5": "Configure automatic screen lock after 5 minutes inactivity. Deploy on all HMIs and engineering workstations.",
    "SR 2.6": "Configure remote session timeout at 15 minutes. Implement session monitoring for remote access connections.",
    "SR 2.7": "Configure maximum concurrent sessions per user. Implement session tracking and automated conflict resolution.",
    "SR 2.8": "Deploy centralized SIEM. Configure audit policies for authentication, authorization, and configuration changes.",
    "SR 2.9": "Allocate dedicated log storage. Implement log rotation with minimum 90-day retention. Deploy log forwarding.",
    "SR 2.10": "Configure alerts for audit system failures. Implement redundant log paths. Test audit failover procedures.",
    "SR 2.11": "Deploy NTP time synchronization across all systems. Configure authenticated NTP. Verify timestamp accuracy.",
    "SR 2.12": "Implement cryptographic audit log signing. Deploy non-repudiation controls for critical operations.",
    "SR 3.1": "Deploy TLS/DTLS for all communications. Implement message authentication codes for industrial protocols.",
    "SR 3.2": "Deploy application whitelisting. Implement network-based IDS/IPS. Establish malware scanning procedures.",
    "SR 3.3": "Implement security function self-tests at startup. Deploy integrity monitoring tools. Schedule periodic verification.",
    "SR 3.4": "Implement file integrity monitoring. Deploy code signing for firmware updates. Configure secure boot.",
    "SR 3.5": "Implement input validation on all external interfaces. Deploy protocol-aware filtering for industrial protocols.",
    "SR 3.6": "Configure safe-state defaults for all outputs. Implement watchdog timers. Test fail-safe behavior.",
    "SR 3.7": "Implement structured error handling that sanitizes error messages. Remove debug information from production.",
    "SR 3.8": "Implement session tokens with cryptographic binding. Deploy anti-replay mechanisms. Configure session timeouts.",
    "SR 3.9": "Restrict audit log access to read-only for reviewers. Implement tamper-evident logging.",
    "SR 4.1": "Encrypt sensitive data at rest (AES-256) and in transit (TLS 1.3). Implement key management procedures.",
    "SR 4.2": "Implement secure memory/storage wiping on connection termination. Verify data purging procedures.",
    "SR 4.3": "Migrate to NIST/BSI-approved cryptographic algorithms. Implement crypto-agility for future algorithm changes.",
    "SR 5.1": "Implement network segmentation with VLANs and firewalls. Create zone architecture per IEC 62443-3-2.",
    "SR 5.2": "Deploy industrial firewalls at zone boundaries. Configure deny-by-default ACLs. Implement deep packet inspection.",
    "SR 5.3": "Block email, messaging, and social media on control network segments. Implement content filtering.",
    "SR 5.4": "Deploy application sandboxing. Implement separate execution environments for security-critical functions.",
    "SR 6.1": "Ensure audit logs are accessible via read-only interface. Deploy log aggregation and search tools.",
    "SR 6.2": "Deploy SIEM with real-time monitoring. Implement automated alerting for security events. Staff 24/7 SOC or MSSP.",
    "SR 7.1": "Deploy rate limiting and traffic shaping. Implement redundant network paths. Test DoS resilience.",
    "SR 7.2": "Configure resource limits for security processes. Implement monitoring for CPU, memory, and disk usage.",
    "SR 7.3": "Implement automated backup procedures. Test restoration regularly. Maintain offline backup copies.",
    "SR 7.4": "Develop and test recovery procedures. Maintain golden images. Document recovery time objectives.",
    "SR 7.5": "Deploy UPS systems. Test emergency power transitions. Verify security state maintained during switchover.",
    "SR 7.6": "Establish baseline configurations per CIS/NIST guides. Implement configuration compliance scanning.",
    "SR 7.7": "Disable unnecessary services and ports. Implement allowlisting for required protocols only.",
    "SR 7.8": "Deploy automated asset discovery. Maintain component inventory database. Implement change tracking.",
}


@dataclass
class ActionItem:
    """A single remediation action for a gap."""

    sr_id: str
    sr_name: str
    fr_id: str
    gap: int
    current_sl: int
    target_sl: int
    recommended_action: str
    effort: str
    priority: str
    target_date: str = ""
    assigned_to: str = ""
    status: str = "Open"  # Open, In Progress, Completed, Deferred

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sr_id": self.sr_id,
            "sr_name": self.sr_name,
            "fr_id": self.fr_id,
            "gap": self.gap,
            "current_sl": self.current_sl,
            "target_sl": self.target_sl,
            "recommended_action": self.recommended_action,
            "effort": self.effort,
            "priority": self.priority,
            "target_date": self.target_date,
            "assigned_to": self.assigned_to,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionItem":
        return cls(
            sr_id=data["sr_id"],
            sr_name=data["sr_name"],
            fr_id=data["fr_id"],
            gap=data["gap"],
            current_sl=data["current_sl"],
            target_sl=data["target_sl"],
            recommended_action=data.get("recommended_action", ""),
            effort=data.get("effort", "Medium"),
            priority=data.get("priority", "Medium"),
            target_date=data.get("target_date", ""),
            assigned_to=data.get("assigned_to", ""),
            status=data.get("status", "Open"),
        )


@dataclass
class ActionPlan:
    """Complete remediation action plan from an assessment."""

    system_name: str
    assessment_date: str
    sl_target: int
    items: List[ActionItem] = field(default_factory=list)

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def critical_count(self) -> int:
        return sum(1 for item in self.items if item.priority == Priority.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for item in self.items if item.priority == Priority.HIGH)

    @property
    def estimated_total_days(self) -> int:
        return sum(Effort.days(item.effort) for item in self.items)

    def sorted_by_priority(self) -> List[ActionItem]:
        """Return items sorted by priority (Critical first)."""
        return sorted(self.items, key=lambda i: Priority.sort_key(i.priority))

    def by_fr(self) -> Dict[str, List[ActionItem]]:
        """Group action items by FR."""
        grouped: Dict[str, List[ActionItem]] = {}
        for item in self.items:
            grouped.setdefault(item.fr_id, []).append(item)
        return grouped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "assessment_date": self.assessment_date,
            "sl_target": self.sl_target,
            "total_items": self.total_items,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "estimated_total_days": self.estimated_total_days,
            "items": [item.to_dict() for item in self.sorted_by_priority()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionPlan":
        plan = cls(
            system_name=data["system_name"],
            assessment_date=data["assessment_date"],
            sl_target=data["sl_target"],
        )
        for item_data in data.get("items", []):
            plan.items.append(ActionItem.from_dict(item_data))
        return plan


def generate_action_plan(
    result: AssessmentResult,
    business_impact_weights: Optional[Dict[str, float]] = None,
) -> ActionPlan:
    """Generate a remediation action plan from an assessment result.

    Args:
        result: Completed assessment result.
        business_impact_weights: Optional dict of SR_id -> weight (0.0-3.0).
            Defaults to 1.0 for all SRs.

    Returns:
        ActionPlan with prioritized remediation items.
    """
    weights = business_impact_weights or {}
    plan = ActionPlan(
        system_name=result.system_name,
        assessment_date=result.assessment_date,
        sl_target=result.sl_target,
    )

    for fr in result.fr_results:
        for sr in fr.sr_results:
            if sr.gap <= 0:
                continue
            weight = weights.get(sr.sr_id, 1.0)
            effort = Effort.from_gap(sr.gap, sr.sr_id)
            priority = Priority.from_gap_and_weight(sr.gap, weight)
            action_text = _SR_ACTIONS.get(
                sr.sr_id,
                f"Remediate {sr.sr_id} ({sr.sr_name}) to achieve SL-{sr.sl_target}.",
            )

            plan.items.append(
                ActionItem(
                    sr_id=sr.sr_id,
                    sr_name=sr.sr_name,
                    fr_id=fr.fr_id,
                    gap=sr.gap,
                    current_sl=sr.sl_achieved,
                    target_sl=sr.sl_target,
                    recommended_action=action_text,
                    effort=effort,
                    priority=priority,
                )
            )

    return plan


def generate_timeline(
    plan: ActionPlan,
    start_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Generate a Gantt-style timeline for the action plan.

    Schedules items by priority (Critical first), assigning dates
    sequentially. Returns a list of timeline entries.
    """
    if start_date is None:
        start_date = date.today()

    timeline: List[Dict[str, Any]] = []
    current_date = start_date

    for item in plan.sorted_by_priority():
        duration = Effort.days(item.effort)
        end_date = current_date + timedelta(days=duration)
        timeline.append({
            "sr_id": item.sr_id,
            "sr_name": item.sr_name,
            "priority": item.priority,
            "effort": item.effort,
            "start_date": current_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": duration,
        })
        # Allow some overlap: next item starts halfway through
        current_date = current_date + timedelta(days=max(1, duration // 2))

    return timeline
