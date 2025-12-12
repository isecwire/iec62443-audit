"""Custom Textual widgets for the IEC 62443 audit TUI.

Includes spider chart, compliance progress bars, gap summary,
and navigation helpers.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, ProgressBar, Label
from textual.widget import Widget

from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult


# ---------------------------------------------------------------------------
# Spider chart widget (ASCII radial chart)
# ---------------------------------------------------------------------------

class SpiderChart(Static):
    """ASCII spider chart showing SL-Achieved vs SL-Target per FR."""

    def __init__(
        self,
        fr_results: list[FRResult],
        sl_target: int = 2,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.fr_results = fr_results
        self.sl_target = sl_target

    def render(self) -> str:
        lines = ["SL-Achieved vs SL-Target per FR", ""]
        max_sl = 4
        bar_width = 28

        for fr in self.fr_results:
            avg = fr.sl_achieved_avg
            target = self.sl_target
            achieved_bars = int(avg / max_sl * bar_width)
            target_pos = int(target / max_sl * bar_width)

            bar_chars = []
            for i in range(bar_width):
                if i == target_pos:
                    bar_chars.append("|")
                elif i < achieved_bars:
                    bar_chars.append("=")
                else:
                    bar_chars.append(".")

            bar = "".join(bar_chars)
            status = "OK" if fr.sl_achieved >= target else f"GAP-{target - fr.sl_achieved}"
            lines.append(f"  {fr.abbreviation:>4} [{bar}] SL-{fr.sl_achieved} {status}")

        lines.append("")
        lines.append("  = achieved  . gap  | target")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Compliance bars widget
# ---------------------------------------------------------------------------

class ComplianceBars(Static):
    """Compliance percentage bars per FR."""

    def __init__(self, fr_results: list[FRResult], **kwargs) -> None:
        super().__init__(**kwargs)
        self.fr_results = fr_results

    def render(self) -> str:
        lines = ["Compliance by FR", ""]
        bar_width = 25

        for fr in self.fr_results:
            pct = fr.compliance_pct
            filled = int(pct / 100 * bar_width)
            empty = bar_width - filled
            bar = "=" * filled + "." * empty
            lines.append(f"  {fr.abbreviation:>4} [{bar}] {pct:5.1f}%")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gap summary widget
# ---------------------------------------------------------------------------

class GapSummary(Static):
    """Table-like summary of all gaps."""

    def __init__(self, result: AssessmentResult, **kwargs) -> None:
        super().__init__(**kwargs)
        self.result = result

    def render(self) -> str:
        lines = [
            f"Gap Summary: {self.result.total_gaps} gaps across "
            f"{self.result.total_srs} SRs",
            "",
            f"  {'SR':<10} {'Name':<30} {'SL-A':>5} {'SL-T':>5} {'Gap':>5}",
            "  " + "-" * 57,
        ]

        for fr in self.result.fr_results:
            for sr in fr.sr_results:
                if sr.gap > 0:
                    name = sr.sr_name[:28]
                    lines.append(
                        f"  {sr.sr_id:<10} {name:<30} "
                        f"{sr.sl_achieved:>5} {sr.sl_target:>5} "
                        f"{'-' + str(sr.gap):>5}"
                    )

        if self.result.total_gaps == 0:
            lines.append("  No gaps found -- all SRs meet target.")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Overall score widget
# ---------------------------------------------------------------------------

class OverallScore(Static):
    """Running score and progress display."""

    def __init__(
        self,
        result: AssessmentResult | None = None,
        completed: int = 0,
        total: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.result = result
        self.completed = completed
        self.total = total

    def render(self) -> str:
        lines = ["Assessment Progress", ""]
        if self.total > 0:
            pct = self.completed / self.total * 100
            lines.append(f"  Progress: {self.completed}/{self.total} ({pct:.0f}%)")
        if self.result:
            lines.append(f"  Overall SL: {self.result.overall_sl}")
            lines.append(f"  Compliance: {self.result.overall_compliance_pct:.1f}%")
            lines.append(f"  Gaps: {self.result.total_gaps}")
        else:
            lines.append("  (assessment in progress)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Navigation hints
# ---------------------------------------------------------------------------

class NavigationHints(Static):
    """Bottom bar with keyboard navigation hints."""

    DEFAULT_CSS = """
    NavigationHints {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text-muted;
    }
    """

    def render(self) -> str:
        return (
            " Tab=switch view | Enter=confirm | n/p=next/prev SR | "
            "Ctrl+S=save | Ctrl+E=export | q=quit"
        )
