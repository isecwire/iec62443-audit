"""Interactive assessor that walks through IEC 62443 system/component requirements.

Uses Rich for formatted prompts, progress tracking, and color-coded output
during the interactive assessment session. Supports both IEC 62443-3-3
(system-level) and IEC 62443-4-2 (component-level) assessments.
"""

from __future__ import annotations

from datetime import date

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from iec62443_audit.requirements import (
    FOUNDATIONAL_REQUIREMENTS,
    FoundationalRequirement,
    total_sr_count,
)
from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult

console = Console()


def _sl_color(sl: int, target: int) -> str:
    """Return a rich color name based on SL vs target."""
    if sl >= target:
        return "green"
    elif sl >= target - 1:
        return "yellow"
    return "red"


class InteractiveAssessor:
    """Walks the user through each SR/CR and collects SL ratings."""

    def __init__(
        self,
        sl_target: int = 2,
        standard: str = "iec62443-3-3",
    ) -> None:
        self.sl_target = sl_target
        self.standard = standard

    def _get_requirements(self):
        """Return the appropriate requirements for the selected standard."""
        if self.standard == "iec62443-4-2":
            from iec62443_audit.standards.iec62443_4_2 import COMPONENT_REQUIREMENTS
            return COMPONENT_REQUIREMENTS
        return FOUNDATIONAL_REQUIREMENTS

    def _get_total(self) -> int:
        """Return total requirement count."""
        if self.standard == "iec62443-4-2":
            from iec62443_audit.standards.iec62443_4_2 import total_cr_count
            return total_cr_count()
        return total_sr_count()

    def _get_sub_requirements(self, fr):
        """Get sub-requirements from an FR (SRs or CRs)."""
        if self.standard == "iec62443-4-2":
            return fr.component_requirements
        return fr.system_requirements

    def run(self) -> AssessmentResult:
        """Run the full interactive assessment and return results."""
        std_label = (
            "IEC 62443-4-2 Component" if self.standard == "iec62443-4-2"
            else "IEC 62443-3-3 System"
        )

        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]{std_label} Security Level Assessment[/]\n"
                "This tool will walk you through each requirement\n"
                "across all 7 Foundational Requirements.",
                border_style="cyan",
            )
        )
        console.print()

        system_name = Prompt.ask(
            "[bold]System / zone under assessment",
            default="Industrial Control System",
        )
        assessor_name = Prompt.ask(
            "[bold]Assessor name",
            default="Security Assessor",
        )
        self.sl_target = IntPrompt.ask(
            "[bold]Target Security Level (SL-T)",
            default=self.sl_target,
            choices=["1", "2", "3", "4"],
        )

        assessment_date = date.today().isoformat()
        requirements = self._get_requirements()
        total = self._get_total()
        completed = 0

        result = AssessmentResult(
            system_name=system_name,
            assessor_name=assessor_name,
            assessment_date=assessment_date,
            sl_target=self.sl_target,
        )

        for fr in requirements:
            sub_reqs = self._get_sub_requirements(fr)
            fr_result = self._assess_fr(fr, sub_reqs, completed, total)
            result.fr_results.append(fr_result)
            completed += len(sub_reqs)

        console.print()
        console.print(
            Panel.fit(
                "[bold green]Assessment complete![/]\n"
                f"Assessed {total} requirements across 7 FRs.",
                border_style="green",
            )
        )
        return result

    def _assess_fr(
        self,
        fr,
        sub_requirements: list,
        completed: int,
        total: int,
    ) -> FRResult:
        """Assess all SRs/CRs within a single FR."""
        console.print()
        console.rule(
            f"[bold blue]{fr.id}: {fr.name} ({fr.abbreviation})[/]",
            style="blue",
        )
        console.print(f"[dim]{fr.description}[/]")
        req_type = "component requirements" if self.standard == "iec62443-4-2" else "system requirements"
        console.print(
            f"[dim]({len(sub_requirements)} {req_type})[/]"
        )
        console.print()

        fr_result = FRResult(
            fr_id=fr.id,
            fr_name=fr.name,
            abbreviation=fr.abbreviation,
        )

        for i, sr in enumerate(sub_requirements):
            progress_num = completed + i + 1
            console.print(
                f"  [dim][{progress_num}/{total}][/] "
                f"[bold]{sr.id}[/]: {sr.name}"
            )
            console.print(f"  [dim]{sr.description}[/]")
            console.print(
                f"  [dim]Applicable from SL {sr.sl_capability} | "
                f"Target: SL-{self.sl_target}[/]"
            )

            if sr.sl_capability > self.sl_target:
                console.print(
                    f"  [dim yellow]Skipped (SL capability {sr.sl_capability} "
                    f"> target SL-{self.sl_target})[/]"
                )
                fr_result.sr_results.append(
                    SRResult(
                        sr_id=sr.id,
                        sr_name=sr.name,
                        sl_achieved=self.sl_target,
                        sl_target=self.sl_target,
                        notes="N/A - requirement capability level exceeds target SL",
                    )
                )
                console.print()
                continue

            while True:
                try:
                    sl_input = Prompt.ask(
                        "  [bold cyan]SL-Achieved (0-4)[/]",
                        default="0",
                    )
                    sl_achieved = int(sl_input)
                    if 0 <= sl_achieved <= 4:
                        break
                    console.print("  [red]Please enter a value 0-4[/]")
                except ValueError:
                    console.print("  [red]Please enter a valid number 0-4[/]")

            notes = Prompt.ask("  [dim]Notes (optional)[/]", default="")

            # Optional evidence collection
            evidence_ref = Prompt.ask(
                "  [dim]Evidence reference (document/URL, optional)[/]",
                default="",
            )
            if evidence_ref:
                notes = f"{notes} | Evidence: {evidence_ref}" if notes else f"Evidence: {evidence_ref}"

            color = _sl_color(sl_achieved, self.sl_target)
            gap = max(0, self.sl_target - sl_achieved)
            status = "[green]PASS[/]" if gap == 0 else f"[red]GAP -{gap}[/]"
            console.print(
                f"  [{color}]SL-{sl_achieved}[/] vs SL-{self.sl_target} "
                f"=> {status}"
            )
            console.print()

            fr_result.sr_results.append(
                SRResult(
                    sr_id=sr.id,
                    sr_name=sr.name,
                    sl_achieved=sl_achieved,
                    sl_target=self.sl_target,
                    notes=notes,
                )
            )

        return fr_result
