"""Report generation for IEC 62443 assessments.

Produces:
- Rich console summary (color-coded table)
- JSON export of the full assessment
- HTML report via Jinja2 template
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from iec62443_audit.scoring import AssessmentResult, compare_assessments

console = Console()

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _sl_style(achieved: int, target: int) -> str:
    """Return a rich style string based on SL gap."""
    if achieved >= target:
        return "bold green"
    elif achieved >= target - 1:
        return "bold yellow"
    return "bold red"


def _compliance_style(pct: float) -> str:
    if pct >= 80:
        return "green"
    elif pct >= 50:
        return "yellow"
    return "red"


# ── Console summary ──────────────────────────────────────────────────────

def print_summary(result: AssessmentResult) -> None:
    """Print a rich console summary of the assessment."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold]Assessment Summary: {result.system_name}[/]\n"
            f"Date: {result.assessment_date}  |  "
            f"Assessor: {result.assessor_name}  |  "
            f"Target: SL-{result.sl_target}",
            border_style="cyan",
        )
    )

    # Overall stats
    sl_style = _sl_style(result.overall_sl, result.sl_target)
    console.print(
        f"\n  Overall SL-Achieved: [{sl_style}]SL-{result.overall_sl}[/] "
        f"(target SL-{result.sl_target})"
    )
    c_style = _compliance_style(result.overall_compliance_pct)
    console.print(
        f"  Overall Compliance:  [{c_style}]{result.overall_compliance_pct:.1f}%[/]"
    )
    console.print(f"  Total Gaps:          {result.total_gaps} / {result.total_srs}")

    # FR table
    table = Table(
        title="\nFoundational Requirements",
        show_header=True,
        header_style="bold",
        border_style="dim",
    )
    table.add_column("FR", style="bold", width=5)
    table.add_column("Name", min_width=30)
    table.add_column("SL-A", justify="center", width=6)
    table.add_column("SL-T", justify="center", width=6)
    table.add_column("Compliance", justify="right", width=12)
    table.add_column("Gaps", justify="center", width=6)

    for fr in result.fr_results:
        sl_style = _sl_style(fr.sl_achieved, result.sl_target)
        c_style = _compliance_style(fr.compliance_pct)
        gap_style = "red" if fr.gap_count > 0 else "green"
        table.add_row(
            fr.fr_id,
            f"{fr.fr_name} ({fr.abbreviation})",
            f"[{sl_style}]{fr.sl_achieved}[/]",
            str(result.sl_target),
            f"[{c_style}]{fr.compliance_pct:.0f}%[/]",
            f"[{gap_style}]{fr.gap_count}[/]",
        )

    console.print(table)


def print_gaps(result: AssessmentResult) -> None:
    """Print only the SRs with gaps, for quick remediation reference."""
    gaps = []
    for fr in result.fr_results:
        for sr in fr.sr_results:
            if sr.gap > 0:
                gaps.append((fr.fr_id, sr))
    if not gaps:
        console.print("\n[bold green]No gaps found -- all SRs meet or exceed target.[/]")
        return

    table = Table(
        title="\nGap Analysis -- System Requirements Below Target",
        show_header=True,
        header_style="bold",
        border_style="dim",
    )
    table.add_column("FR", width=5)
    table.add_column("SR", width=8)
    table.add_column("Name", min_width=30)
    table.add_column("Achieved", justify="center", width=10)
    table.add_column("Target", justify="center", width=8)
    table.add_column("Gap", justify="center", width=5)
    table.add_column("Notes", max_width=40)

    for fr_id, sr in gaps:
        table.add_row(
            fr_id,
            sr.sr_id,
            sr.sr_name,
            f"[bold red]SL-{sr.sl_achieved}[/]",
            f"SL-{sr.sl_target}",
            f"[bold red]-{sr.gap}[/]",
            sr.notes or "",
        )

    console.print(table)


# ── JSON export ──────────────────────────────────────────────────────────

def export_json(result: AssessmentResult, path: Path) -> Path:
    """Write the full assessment to a JSON file."""
    data = result.to_dict()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    console.print(f"[green]JSON report saved to:[/] {path}")
    return path


def load_json(path: Path) -> AssessmentResult:
    """Load an assessment from a JSON file."""
    data = json.loads(path.read_text())
    return AssessmentResult.from_dict(data)


# ── HTML report ──────────────────────────────────────────────────────────

def export_html(result: AssessmentResult, path: Path) -> Path:
    """Render the Jinja2 HTML template and write to a file."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("report.html")
    data = result.to_dict()
    html = template.render(**data)
    path.write_text(html, encoding="utf-8")
    console.print(f"[green]HTML report saved to:[/] {path}")
    return path


# ── Comparison report ────────────────────────────────────────────────────

def print_comparison(baseline: AssessmentResult, current: AssessmentResult) -> None:
    """Print a comparison between two assessments."""
    comp = compare_assessments(baseline, current)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Progress Report: {comp['system_name']}[/]\n"
            f"Baseline: {comp['baseline_date']}  ->  "
            f"Current: {comp['current_date']}",
            border_style="cyan",
        )
    )

    delta_sl = comp["overall_sl_delta"]
    delta_c = comp["compliance_delta"]
    sl_arrow = "[green]+{}[/]" if delta_sl > 0 else "[red]{}[/]" if delta_sl < 0 else "[dim]{}[/]"
    c_arrow = "[green]+{}%[/]" if delta_c > 0 else "[red]{}%[/]" if delta_c < 0 else "[dim]{}%[/]"

    console.print(
        f"\n  Overall SL: {comp['overall_sl_baseline']} -> "
        f"{comp['overall_sl_current']} ({sl_arrow.format(delta_sl)})"
    )
    console.print(
        f"  Compliance: {comp['compliance_baseline']}% -> "
        f"{comp['compliance_current']}% ({c_arrow.format(delta_c)})"
    )

    table = Table(
        title="\nFR-Level Progress",
        show_header=True,
        header_style="bold",
        border_style="dim",
    )
    table.add_column("FR", width=5)
    table.add_column("Name", min_width=25)
    table.add_column("Baseline SL", justify="center", width=12)
    table.add_column("Current SL", justify="center", width=11)
    table.add_column("Delta", justify="center", width=7)
    table.add_column("Compliance", justify="right", width=18)

    for fr in comp["foundational_requirements"]:
        d = fr["sl_delta"]
        if d > 0:
            delta_str = f"[bold green]+{d}[/]"
        elif d < 0:
            delta_str = f"[bold red]{d}[/]"
        else:
            delta_str = "[dim]0[/]"

        table.add_row(
            fr["fr_id"],
            fr["fr_name"],
            str(fr["sl_baseline"]),
            str(fr["sl_current"]),
            delta_str,
            f"{fr['compliance_baseline']}% -> {fr['compliance_current']}%",
        )

    console.print(table)

    # Show improved / regressed SRs
    improved = []
    regressed = []
    for fr in comp["foundational_requirements"]:
        for sr in fr["system_requirements"]:
            if sr["status"] == "improved":
                improved.append(f"  [green]+{sr['delta']}[/] {sr['sr_id']}: {sr['sr_name']}")
            elif sr["status"] == "regressed":
                regressed.append(f"  [red]{sr['delta']}[/] {sr['sr_id']}: {sr['sr_name']}")

    if improved:
        console.print(f"\n[bold green]Improved ({len(improved)} SRs):[/]")
        for line in improved:
            console.print(line)
    if regressed:
        console.print(f"\n[bold red]Regressed ({len(regressed)} SRs):[/]")
        for line in regressed:
            console.print(line)
    if not improved and not regressed:
        console.print("\n[dim]No changes between assessments.[/]")
