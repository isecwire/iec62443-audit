"""Textual TUI screens for the IEC 62443 audit tool.

Screens:
- WelcomeScreen: project name, target SL, assessor name
- AssessmentScreen: main assessment with FR sidebar, SR center, score right
- DashboardScreen: spider chart, compliance bars, gap summary
- ActionPlanScreen: sortable gap table with actions and effort
- ComparisonScreen: load two assessments, show deltas
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TextArea,
)

from iec62443_audit.requirements import (
    FOUNDATIONAL_REQUIREMENTS,
    FoundationalRequirement,
    total_sr_count,
)
from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult
from iec62443_audit.tui.widgets import (
    ComplianceBars,
    GapSummary,
    NavigationHints,
    OverallScore,
    SpiderChart,
)


# ---------------------------------------------------------------------------
# Welcome Screen
# ---------------------------------------------------------------------------

class WelcomeScreen(Screen):
    """Initial screen for project setup."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    CSS = """
    WelcomeScreen {
        align: center middle;
    }
    #welcome-box {
        width: 70;
        height: auto;
        border: thick $primary;
        padding: 2 4;
    }
    #welcome-box Label {
        margin-bottom: 1;
    }
    #welcome-box Input {
        margin-bottom: 1;
    }
    #welcome-box Select {
        margin-bottom: 1;
    }
    #start-btn {
        margin-top: 2;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="welcome-box"):
            yield Label("[bold]IEC 62443 Security Level Assessment[/]")
            yield Label("")
            yield Label("System / Zone Name:")
            yield Input(
                placeholder="e.g., Water Treatment Plant Zone A",
                id="system-name",
            )
            yield Label("Assessor Name:")
            yield Input(
                placeholder="e.g., J. Smith",
                id="assessor-name",
            )
            yield Label("Target Security Level:")
            yield Select(
                [(f"SL-{i}", i) for i in range(1, 5)],
                value=2,
                id="sl-target",
            )
            yield Label("Standard:")
            yield Select(
                [
                    ("IEC 62443-3-3 (System)", "iec62443-3-3"),
                    ("IEC 62443-4-2 (Component)", "iec62443-4-2"),
                ],
                value="iec62443-3-3",
                id="standard",
            )
            yield Button("Start Assessment", variant="primary", id="start-btn")
        yield Footer()

    @on(Button.Pressed, "#start-btn")
    def start_assessment(self) -> None:
        system_name = self.query_one("#system-name", Input).value or "ICS Assessment"
        assessor = self.query_one("#assessor-name", Input).value or "Assessor"
        sl_target = self.query_one("#sl-target", Select).value
        standard = self.query_one("#standard", Select).value

        self.app.system_name = system_name
        self.app.assessor_name = assessor
        self.app.sl_target = sl_target
        self.app.standard = standard

        self.app.init_assessment()
        self.app.push_screen("assessment")


# ---------------------------------------------------------------------------
# Assessment Screen
# ---------------------------------------------------------------------------

class AssessmentScreen(Screen):
    """Main assessment view with FR sidebar, SR center, score right."""

    BINDINGS = [
        Binding("n", "next_sr", "Next SR"),
        Binding("p", "prev_sr", "Prev SR"),
        Binding("tab", "switch_view", "Switch View"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+e", "export", "Export"),
    ]

    CSS = """
    AssessmentScreen {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 3fr 1fr;
        grid-rows: 1fr 3;
    }
    #fr-sidebar {
        row-span: 1;
        border: solid $primary;
        padding: 1;
    }
    #sr-center {
        row-span: 1;
        border: solid $accent;
        padding: 1 2;
        overflow-y: auto;
    }
    #score-panel {
        row-span: 1;
        border: solid $success;
        padding: 1;
    }
    #nav-bar {
        column-span: 3;
        dock: bottom;
    }
    .fr-item-pass {
        color: green;
    }
    .fr-item-partial {
        color: yellow;
    }
    .fr-item-fail {
        color: red;
    }
    .fr-item-pending {
        color: $text-muted;
    }
    #rating-input {
        margin-top: 1;
        width: 20;
    }
    #notes-input {
        margin-top: 1;
        height: 3;
    }
    #confirm-btn {
        margin-top: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_fr_idx = 0
        self.current_sr_idx = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="fr-sidebar"):
            yield Label("[bold]Foundational Requirements[/]")
            yield Static(id="fr-list")

        with VerticalScroll(id="sr-center"):
            yield Label("[bold]System Requirement[/]", id="sr-title")
            yield Static(id="sr-description")
            yield Label("SL-Achieved (0-4):")
            yield Input(placeholder="0", id="rating-input", type="integer")
            yield Label("Notes:")
            yield Input(placeholder="Optional notes...", id="notes-input")
            yield Button("Confirm Rating", variant="primary", id="confirm-btn")

        with Vertical(id="score-panel"):
            yield OverallScore(
                result=self.app.assessment if hasattr(self.app, 'assessment') else None,
                completed=0,
                total=total_sr_count(),
                id="score-widget",
            )

        yield NavigationHints(id="nav-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._update_display()

    def _get_frs(self):
        return FOUNDATIONAL_REQUIREMENTS

    def _current_fr(self):
        frs = self._get_frs()
        if self.current_fr_idx < len(frs):
            return frs[self.current_fr_idx]
        return None

    def _current_sr(self):
        fr = self._current_fr()
        if fr and self.current_sr_idx < len(fr.system_requirements):
            return fr.system_requirements[self.current_sr_idx]
        return None

    def _update_display(self) -> None:
        # Update FR sidebar
        frs = self._get_frs()
        fr_lines = []
        for i, fr in enumerate(frs):
            marker = ">>>" if i == self.current_fr_idx else "   "
            # Determine completion status
            fr_result = None
            if hasattr(self.app, 'assessment') and self.app.assessment:
                for fr_r in self.app.assessment.fr_results:
                    if fr_r.fr_id == fr.id:
                        fr_result = fr_r
                        break

            if fr_result and len(fr_result.sr_results) == len(fr.system_requirements):
                if fr_result.compliance_pct >= 100:
                    status = "[green]OK[/]"
                elif fr_result.compliance_pct > 0:
                    status = "[yellow]!![/]"
                else:
                    status = "[red]XX[/]"
            else:
                status = "[dim]..[/]"

            fr_lines.append(f"{marker} {fr.id} {fr.abbreviation:>4} {status}")

        self.query_one("#fr-list", Static).update("\n".join(fr_lines))

        # Update SR center
        sr = self._current_sr()
        fr = self._current_fr()
        if sr and fr:
            self.query_one("#sr-title", Label).update(
                f"[bold]{sr.id}: {sr.name}[/]"
            )
            desc = (
                f"{fr.id}: {fr.name}\n\n"
                f"{sr.description}\n\n"
                f"Applicable from SL-{sr.sl_capability} | "
                f"Target: SL-{self.app.sl_target}"
            )
            self.query_one("#sr-description", Static).update(desc)

        # Update score
        completed = 0
        if hasattr(self.app, 'assessment') and self.app.assessment:
            completed = sum(
                len(fr_r.sr_results) for fr_r in self.app.assessment.fr_results
            )
        self.query_one("#score-widget", OverallScore).completed = completed
        self.query_one("#score-widget", OverallScore).total = total_sr_count()
        self.query_one("#score-widget", OverallScore).result = (
            self.app.assessment if hasattr(self.app, 'assessment') else None
        )
        self.query_one("#score-widget", OverallScore).refresh()

    @on(Button.Pressed, "#confirm-btn")
    def confirm_rating(self) -> None:
        sr = self._current_sr()
        fr = self._current_fr()
        if not sr or not fr:
            return

        rating_input = self.query_one("#rating-input", Input)
        notes_input = self.query_one("#notes-input", Input)

        try:
            sl_achieved = int(rating_input.value or "0")
            sl_achieved = max(0, min(4, sl_achieved))
        except ValueError:
            sl_achieved = 0

        notes = notes_input.value or ""

        # Record the rating
        self.app.record_rating(fr.id, sr.id, sr.name, sl_achieved, notes)

        # Clear inputs
        rating_input.value = ""
        notes_input.value = ""

        # Advance to next SR
        self.action_next_sr()

    def action_next_sr(self) -> None:
        fr = self._current_fr()
        if fr and self.current_sr_idx < len(fr.system_requirements) - 1:
            self.current_sr_idx += 1
        else:
            # Move to next FR
            frs = self._get_frs()
            if self.current_fr_idx < len(frs) - 1:
                self.current_fr_idx += 1
                self.current_sr_idx = 0
            else:
                # Assessment complete
                self.app.push_screen("dashboard")
                return
        self._update_display()

    def action_prev_sr(self) -> None:
        if self.current_sr_idx > 0:
            self.current_sr_idx -= 1
        elif self.current_fr_idx > 0:
            self.current_fr_idx -= 1
            fr = self._current_fr()
            if fr:
                self.current_sr_idx = len(fr.system_requirements) - 1
        self._update_display()

    def action_switch_view(self) -> None:
        self.app.push_screen("dashboard")

    def action_save(self) -> None:
        self.app.save_assessment()
        self.notify("Assessment saved.")

    def action_export(self) -> None:
        self.app.export_assessment()
        self.notify("Assessment exported.")


# ---------------------------------------------------------------------------
# Dashboard Screen
# ---------------------------------------------------------------------------

class DashboardScreen(Screen):
    """Dashboard with spider chart, compliance bars, gap summary."""

    BINDINGS = [
        Binding("tab", "switch_view", "Assessment"),
        Binding("a", "action_plan", "Action Plan"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+e", "export", "Export"),
        Binding("escape", "back", "Back"),
    ]

    CSS = """
    DashboardScreen {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
    }
    #spider-panel {
        border: solid $primary;
        padding: 1;
    }
    #compliance-panel {
        border: solid $success;
        padding: 1;
    }
    #gap-panel {
        column-span: 2;
        border: solid $warning;
        padding: 1;
        overflow-y: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        result = self.app.assessment
        fr_results = result.fr_results if result else []

        with Vertical(id="spider-panel"):
            yield SpiderChart(
                fr_results=fr_results,
                sl_target=self.app.sl_target,
            )

        with Vertical(id="compliance-panel"):
            yield ComplianceBars(fr_results=fr_results)

        with VerticalScroll(id="gap-panel"):
            if result:
                yield GapSummary(result=result)
            else:
                yield Static("No assessment data yet.")

        yield NavigationHints()
        yield Footer()

    def action_switch_view(self) -> None:
        self.app.pop_screen()

    def action_action_plan(self) -> None:
        self.app.push_screen("action_plan")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_save(self) -> None:
        self.app.save_assessment()
        self.notify("Assessment saved.")

    def action_export(self) -> None:
        self.app.export_assessment()
        self.notify("Assessment exported.")


# ---------------------------------------------------------------------------
# Action Plan Screen
# ---------------------------------------------------------------------------

class ActionPlanScreen(Screen):
    """Action plan view with sortable gap table."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("tab", "switch_view", "Dashboard"),
    ]

    CSS = """
    ActionPlanScreen {
        overflow-y: auto;
    }
    #plan-table {
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with VerticalScroll(id="plan-table"):
            result = self.app.assessment
            if result and result.total_gaps > 0:
                from iec62443_audit.action_plan import generate_action_plan
                plan = generate_action_plan(result)

                lines = [
                    f"Remediation Action Plan: {plan.system_name}",
                    f"Total: {plan.total_items} | "
                    f"Critical: {plan.critical_count} | "
                    f"High: {plan.high_count} | "
                    f"Est: ~{plan.estimated_total_days} days",
                    "",
                    f"{'#':>3} {'SR':<10} {'Gap':>4} {'Priority':<10} "
                    f"{'Effort':<8} Action",
                    "-" * 80,
                ]

                for i, item in enumerate(plan.sorted_by_priority(), 1):
                    action = item.recommended_action[:55]
                    lines.append(
                        f"{i:>3} {item.sr_id:<10} -{item.gap:>3} "
                        f"{item.priority:<10} {item.effort:<8} {action}"
                    )

                yield Static("\n".join(lines))
            else:
                yield Static("No gaps found -- no action plan needed.")

        yield NavigationHints()
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_switch_view(self) -> None:
        self.app.pop_screen()


# ---------------------------------------------------------------------------
# Comparison Screen
# ---------------------------------------------------------------------------

class ComparisonScreen(Screen):
    """Load two assessments and display improvements/regressions."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    CSS = """
    ComparisonScreen {
        overflow-y: auto;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        baseline: AssessmentResult | None = None,
        current: AssessmentResult | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.baseline = baseline
        self.current = current

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with VerticalScroll():
            if self.baseline and self.current:
                from iec62443_audit.scoring import compare_assessments
                comp = compare_assessments(self.baseline, self.current)

                lines = [
                    f"Assessment Comparison: {comp['system_name']}",
                    f"{comp['baseline_date']} --> {comp['current_date']}",
                    "",
                    f"Overall SL: {comp['overall_sl_baseline']} -> "
                    f"{comp['overall_sl_current']} (delta: {comp['overall_sl_delta']:+d})",
                    f"Compliance: {comp['compliance_baseline']}% -> "
                    f"{comp['compliance_current']}% (delta: {comp['compliance_delta']:+.1f}%)",
                    "",
                    f"{'FR':<5} {'Name':<30} {'Before':>7} {'After':>7} {'Delta':>7}",
                    "-" * 60,
                ]

                improved = []
                regressed = []

                for fr in comp["foundational_requirements"]:
                    d = fr["sl_delta"]
                    lines.append(
                        f"{fr['fr_id']:<5} {fr['fr_name']:<30} "
                        f"SL-{fr['sl_baseline']:>4} SL-{fr['sl_current']:>4} "
                        f"{d:>+5d}"
                    )
                    for sr in fr["system_requirements"]:
                        if sr["status"] == "improved":
                            improved.append(
                                f"  +{sr['delta']} {sr['sr_id']}: {sr['sr_name']}"
                            )
                        elif sr["status"] == "regressed":
                            regressed.append(
                                f"  {sr['delta']} {sr['sr_id']}: {sr['sr_name']}"
                            )

                if improved:
                    lines.extend(["", f"Improved ({len(improved)} SRs):"] + improved)
                if regressed:
                    lines.extend(["", f"Regressed ({len(regressed)} SRs):"] + regressed)
                if not improved and not regressed:
                    lines.append("\nNo changes between assessments.")

                yield Static("\n".join(lines))
            else:
                yield Static("No comparison data loaded.")

        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()
