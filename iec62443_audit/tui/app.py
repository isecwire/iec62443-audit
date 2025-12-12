"""Main Textual App class for the IEC 62443 audit TUI."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from textual.app import App
from textual.binding import Binding

from iec62443_audit.requirements import FOUNDATIONAL_REQUIREMENTS, total_sr_count
from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult
from iec62443_audit.report import export_json, export_html


class AuditApp(App):
    """IEC 62443 Security Level Assessment TUI."""

    TITLE = "IEC 62443 Audit Tool"
    SUB_TITLE = "Security Level Assessment"

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(
        self,
        sl_target: int = 2,
        system_name: str = "",
        assessor_name: str = "",
        standard: str = "iec62443-3-3",
        load_file: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sl_target = sl_target
        self.system_name = system_name
        self.assessor_name = assessor_name
        self.standard = standard
        self.load_file = load_file
        self.assessment: Optional[AssessmentResult] = None
        self._fr_results_map: dict[str, FRResult] = {}

    def on_mount(self) -> None:
        from iec62443_audit.tui.screens import (
            WelcomeScreen,
            AssessmentScreen,
            DashboardScreen,
            ActionPlanScreen,
            ComparisonScreen,
        )

        self.install_screen(WelcomeScreen(), "welcome")
        self.install_screen(AssessmentScreen(), "assessment")
        self.install_screen(DashboardScreen(), "dashboard")
        self.install_screen(ActionPlanScreen(), "action_plan")

        if self.load_file:
            self._load_from_file(self.load_file)
            self.push_screen("dashboard")
        elif self.system_name:
            self.init_assessment()
            self.push_screen("assessment")
        else:
            self.push_screen("welcome")

    def init_assessment(self) -> None:
        """Initialize a new assessment."""
        self.assessment = AssessmentResult(
            system_name=self.system_name,
            assessor_name=self.assessor_name,
            assessment_date=date.today().isoformat(),
            sl_target=self.sl_target,
        )
        self._fr_results_map = {}

    def record_rating(
        self,
        fr_id: str,
        sr_id: str,
        sr_name: str,
        sl_achieved: int,
        notes: str = "",
    ) -> None:
        """Record an SL rating for an SR."""
        if not self.assessment:
            return

        # Get or create FR result
        if fr_id not in self._fr_results_map:
            for fr in FOUNDATIONAL_REQUIREMENTS:
                if fr.id == fr_id:
                    fr_result = FRResult(
                        fr_id=fr.id,
                        fr_name=fr.name,
                        abbreviation=fr.abbreviation,
                    )
                    self._fr_results_map[fr_id] = fr_result
                    self.assessment.fr_results.append(fr_result)
                    break

        fr_result = self._fr_results_map.get(fr_id)
        if not fr_result:
            return

        # Check if SR already rated (update it)
        for existing in fr_result.sr_results:
            if existing.sr_id == sr_id:
                existing.sl_achieved = sl_achieved
                existing.notes = notes
                return

        # Add new SR result
        fr_result.sr_results.append(
            SRResult(
                sr_id=sr_id,
                sr_name=sr_name,
                sl_achieved=sl_achieved,
                sl_target=self.sl_target,
                notes=notes,
            )
        )

    def save_assessment(self, filename: str = "assessment.json") -> None:
        """Save current assessment to JSON."""
        if not self.assessment:
            return
        path = Path(filename)
        export_json(self.assessment, path)

    def export_assessment(
        self,
        json_path: str = "assessment.json",
        html_path: str = "assessment.html",
    ) -> None:
        """Export assessment to JSON and HTML."""
        if not self.assessment:
            return
        export_json(self.assessment, Path(json_path))
        export_html(self.assessment, Path(html_path))

    def _load_from_file(self, filepath: str) -> None:
        """Load an existing assessment from JSON."""
        from iec62443_audit.report import load_json
        self.assessment = load_json(Path(filepath))
        self.system_name = self.assessment.system_name
        self.assessor_name = self.assessment.assessor_name
        self.sl_target = self.assessment.sl_target

        # Rebuild FR map
        self._fr_results_map = {
            fr.fr_id: fr for fr in self.assessment.fr_results
        }
