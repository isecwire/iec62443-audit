"""Rich CLI display module for iec62443-audit.

Provides colored FR/SR tables with status badges, spider/radar charts
(ASCII art), gap analysis heatmaps, side-by-side comparison, progress
tracking, and action plan display.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult

console = Console()


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _sl_badge(achieved: int, target: int) -> str:
    """Return a rich-formatted SL badge string."""
    if achieved >= target:
        return f"[bold green]SL-{achieved} [OK][/]"
    elif achieved >= target - 1:
        return f"[bold yellow]SL-{achieved} [!!][/]"
    return f"[bold red]SL-{achieved} [XX][/]"


def _compliance_bar(pct: float, width: int = 20) -> str:
    """Return a text-based progress bar."""
    filled = int(pct / 100 * width)
    empty = width - filled
    if pct >= 80:
        color = "green"
    elif pct >= 50:
        color = "yellow"
    else:
        color = "red"
    bar = f"[{color}]{'=' * filled}[/][dim]{'.' * empty}[/]"
    return f"{bar} {pct:.0f}%"


def _priority_style(priority: str) -> str:
    """Return rich style for a priority level."""
    return {
        "Critical": "bold red",
        "High": "red",
        "Medium": "yellow",
        "Low": "green",
    }.get(priority, "white")


def _effort_style(effort: str) -> str:
    return {
        "Low": "green",
        "Medium": "yellow",
        "High": "red",
    }.get(effort, "white")


# ---------------------------------------------------------------------------
# FR/SR Tables
# ---------------------------------------------------------------------------

def print_fr_table(result: AssessmentResult) -> None:
    """Print a colored FR summary table with status badges."""
    table = Table(
        title=f"\n[bold]Foundational Requirements -- {result.system_name}[/]",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("FR", style="bold", width=5)
    table.add_column("Name", min_width=32)
    table.add_column("Status", justify="center", width=14)
    table.add_column("SL-T", justify="center", width=5)
    table.add_column("Compliance", width=28)
    table.add_column("Gaps", justify="center", width=5)

    for fr in result.fr_results:
        badge = _sl_badge(fr.sl_achieved, result.sl_target)
        bar = _compliance_bar(fr.compliance_pct)
        gap_str = (
            f"[bold red]{fr.gap_count}[/]"
            if fr.gap_count > 0
            else "[green]0[/]"
        )
        table.add_row(
            fr.fr_id,
            f"{fr.fr_name} ({fr.abbreviation})",
            badge,
            str(result.sl_target),
            bar,
            gap_str,
        )

    console.print(table)


def print_sr_table(fr: FRResult, target: int) -> None:
    """Print detailed SR table for a single FR."""
    table = Table(
        title=f"\n[bold]{fr.fr_id}: {fr.fr_name} ({fr.abbreviation})[/]",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("SR", width=8)
    table.add_column("Name", min_width=30)
    table.add_column("Status", justify="center", width=14)
    table.add_column("Gap", justify="center", width=6)
    table.add_column("Notes", max_width=35)

    for sr in fr.sr_results:
        badge = _sl_badge(sr.sl_achieved, target)
        gap_str = (
            f"[bold red]-{sr.gap}[/]" if sr.gap > 0 else "[green]OK[/]"
        )
        table.add_row(
            sr.sr_id,
            sr.sr_name,
            badge,
            gap_str,
            sr.notes or "[dim]--[/]",
        )

    console.print(table)


def print_full_assessment(result: AssessmentResult) -> None:
    """Print complete assessment with all FR and SR details."""
    print_header(result)
    print_stats_cards(result)
    print_fr_table(result)
    for fr in result.fr_results:
        print_sr_table(fr, result.sl_target)


# ---------------------------------------------------------------------------
# Stats cards
# ---------------------------------------------------------------------------

def print_header(result: AssessmentResult) -> None:
    """Print the assessment header panel."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]IEC 62443 Security Level Assessment[/]\n"
            f"[bold]{result.system_name}[/]\n\n"
            f"Date: {result.assessment_date}  |  "
            f"Assessor: {result.assessor_name}  |  "
            f"Target: SL-{result.sl_target}",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_stats_cards(result: AssessmentResult) -> None:
    """Print summary statistics as card-style boxes."""
    sl_color = "green" if result.overall_sl >= result.sl_target else "red"
    c_color = "green" if result.overall_compliance_pct >= 80 else "yellow" if result.overall_compliance_pct >= 50 else "red"
    g_color = "green" if result.total_gaps == 0 else "red"

    cards = [
        Panel(
            f"[{sl_color} bold]SL-{result.overall_sl}[/]\n[dim]Overall Achieved[/]",
            border_style=sl_color,
            width=22,
        ),
        Panel(
            f"[bold]SL-{result.sl_target}[/]\n[dim]Target Level[/]",
            border_style="cyan",
            width=22,
        ),
        Panel(
            f"[{c_color} bold]{result.overall_compliance_pct:.1f}%[/]\n[dim]Compliance[/]",
            border_style=c_color,
            width=22,
        ),
        Panel(
            f"[{g_color} bold]{result.total_gaps}[/]\n[dim]Total Gaps[/]",
            border_style=g_color,
            width=22,
        ),
    ]
    console.print(Columns(cards, padding=(0, 1)))


# ---------------------------------------------------------------------------
# Spider / Radar chart (ASCII art)
# ---------------------------------------------------------------------------

def print_spider_chart(
    result: AssessmentResult,
    title: str = "SL-Achieved vs SL-Target per FR",
) -> None:
    """Print an ASCII spider/radar chart showing SL per FR.

    Renders a simple text-based radial chart with achieved vs target
    overlay.
    """
    frs = result.fr_results
    if not frs:
        return

    console.print(f"\n[bold cyan]{title}[/]")
    console.print()

    # Use a bar-style radar representation
    max_sl = 4
    bar_width = 30

    for fr in frs:
        achieved = fr.sl_achieved
        target = result.sl_target
        avg = fr.sl_achieved_avg

        achieved_bars = int(avg / max_sl * bar_width)
        target_pos = int(target / max_sl * bar_width)

        # Build the bar
        bar_chars = []
        for i in range(bar_width):
            if i < achieved_bars and i < target_pos:
                bar_chars.append("[green]=[/]")
            elif i < achieved_bars:
                bar_chars.append("[blue]=[/]")
            elif i < target_pos:
                bar_chars.append("[red].[/]")
            else:
                bar_chars.append("[dim].[/]")

        # Insert target marker
        if target_pos < bar_width:
            bar_chars[target_pos] = "[bold white]|[/]"

        bar = "".join(bar_chars)
        label = f"{fr.abbreviation:>4}"
        value = f"SL-{achieved} (avg {avg:.1f})"

        if achieved >= target:
            status = "[green]PASS[/]"
        else:
            status = f"[red]GAP -{target - achieved}[/]"

        console.print(f"  {label} {bar} {value} {status}")

    console.print()
    console.print("  [dim]Legend: [green]=[/]=achieved [red].[/]=gap [white]|[/]=target[/]")


# ---------------------------------------------------------------------------
# Gap analysis heatmap (ASCII)
# ---------------------------------------------------------------------------

def print_gap_heatmap(result: AssessmentResult) -> None:
    """Print an ASCII heatmap of gaps across all FRs and SRs."""
    console.print("\n[bold cyan]Gap Analysis Heatmap[/]")
    console.print("[dim]Each cell = one SR. Color intensity = gap severity.[/]\n")

    for fr in result.fr_results:
        cells = []
        for sr in fr.sr_results:
            if sr.gap == 0:
                cells.append("[on green] [/]")
            elif sr.gap == 1:
                cells.append("[on yellow] [/]")
            elif sr.gap == 2:
                cells.append("[on red] [/]")
            else:
                cells.append("[on bright_red] [/]")

        cell_str = "".join(cells)
        pct = fr.compliance_pct
        console.print(
            f"  {fr.abbreviation:>4} {cell_str} "
            f"{pct:5.0f}% ({fr.gap_count} gaps)"
        )

    console.print()
    console.print(
        "  [dim]Legend: "
        "[on green] [/]=OK "
        "[on yellow] [/]=gap 1 "
        "[on red] [/]=gap 2 "
        "[on bright_red] [/]=gap 3+[/]"
    )


# ---------------------------------------------------------------------------
# Side-by-side comparison
# ---------------------------------------------------------------------------

def print_side_by_side(
    baseline: AssessmentResult,
    current: AssessmentResult,
) -> None:
    """Print a side-by-side comparison of two assessments."""
    from iec62443_audit.scoring import compare_assessments

    comp = compare_assessments(baseline, current)

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Assessment Comparison: {comp['system_name']}[/]\n"
            f"{comp['baseline_date']} --> {comp['current_date']}",
            border_style="cyan",
        )
    )

    # Overall delta
    delta_sl = comp["overall_sl_delta"]
    delta_c = comp["compliance_delta"]
    sl_style = "green" if delta_sl > 0 else "red" if delta_sl < 0 else "dim"
    c_style = "green" if delta_c > 0 else "red" if delta_c < 0 else "dim"

    console.print(
        f"\n  Overall SL: {comp['overall_sl_baseline']} -> "
        f"{comp['overall_sl_current']} "
        f"([{sl_style}]{'+' if delta_sl > 0 else ''}{delta_sl}[/])"
    )
    console.print(
        f"  Compliance: {comp['compliance_baseline']}% -> "
        f"{comp['compliance_current']}% "
        f"([{c_style}]{'+' if delta_c > 0 else ''}{delta_c}%[/])"
    )

    # FR comparison table
    table = Table(
        title="\nFR-Level Comparison",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("FR", width=5, style="bold")
    table.add_column("Name", min_width=25)
    table.add_column("Baseline", justify="center", width=10)
    table.add_column("Current", justify="center", width=10)
    table.add_column("Delta", justify="center", width=8)
    table.add_column("Compliance", width=22)

    for fr in comp["foundational_requirements"]:
        d = fr["sl_delta"]
        if d > 0:
            delta_str = f"[bold green]+{d}[/]"
        elif d < 0:
            delta_str = f"[bold red]{d}[/]"
        else:
            delta_str = "[dim]0[/]"

        c_before = fr["compliance_baseline"]
        c_after = fr["compliance_current"]
        c_delta = c_after - c_before
        c_style = "green" if c_delta > 0 else "red" if c_delta < 0 else "dim"

        table.add_row(
            fr["fr_id"],
            fr["fr_name"],
            f"SL-{fr['sl_baseline']}",
            f"SL-{fr['sl_current']}",
            delta_str,
            f"{c_before}% -> [{c_style}]{c_after}%[/]",
        )

    console.print(table)

    # Changed SRs
    improved = []
    regressed = []
    for fr in comp["foundational_requirements"]:
        for sr in fr["system_requirements"]:
            if sr["status"] == "improved":
                improved.append((sr["sr_id"], sr["sr_name"], sr["delta"]))
            elif sr["status"] == "regressed":
                regressed.append((sr["sr_id"], sr["sr_name"], sr["delta"]))

    if improved:
        console.print(f"\n[bold green]Improved ({len(improved)} SRs):[/]")
        for sr_id, sr_name, delta in improved:
            console.print(f"  [green]+{delta}[/] {sr_id}: {sr_name}")
    if regressed:
        console.print(f"\n[bold red]Regressed ({len(regressed)} SRs):[/]")
        for sr_id, sr_name, delta in regressed:
            console.print(f"  [red]{delta}[/] {sr_id}: {sr_name}")
    if not improved and not regressed:
        console.print("\n[dim]No changes detected.[/]")


# ---------------------------------------------------------------------------
# Action plan display
# ---------------------------------------------------------------------------

def print_action_plan(plan: "ActionPlan") -> None:
    """Print a formatted action plan table."""
    from iec62443_audit.action_plan import ActionPlan

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Remediation Action Plan: {plan.system_name}[/]\n"
            f"Total items: {plan.total_items}  |  "
            f"Critical: {plan.critical_count}  |  "
            f"High: {plan.high_count}  |  "
            f"Est. effort: ~{plan.estimated_total_days} days",
            border_style="red" if plan.critical_count > 0 else "yellow",
        )
    )

    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("#", width=3, justify="right")
    table.add_column("SR", width=8)
    table.add_column("FR", width=5)
    table.add_column("Gap", justify="center", width=5)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Effort", justify="center", width=8)
    table.add_column("Recommended Action", min_width=40, max_width=60)

    for i, item in enumerate(plan.sorted_by_priority(), 1):
        p_style = _priority_style(item.priority)
        e_style = _effort_style(item.effort)
        table.add_row(
            str(i),
            item.sr_id,
            item.fr_id,
            f"[red]-{item.gap}[/]",
            f"[{p_style}]{item.priority}[/]",
            f"[{e_style}]{item.effort}[/]",
            item.recommended_action,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Timeline display
# ---------------------------------------------------------------------------

def print_timeline(timeline: List[Dict[str, Any]]) -> None:
    """Print a Gantt-style ASCII timeline."""
    if not timeline:
        console.print("[dim]No timeline to display.[/]")
        return

    console.print("\n[bold cyan]Remediation Timeline (Gantt)[/]\n")

    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("SR", width=8)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Start", width=12)
    table.add_column("End", width=12)
    table.add_column("Days", justify="center", width=5)
    table.add_column("Timeline", min_width=30)

    # Determine date range for scaling
    from datetime import date as Date

    all_starts = [Date.fromisoformat(t["start_date"]) for t in timeline]
    all_ends = [Date.fromisoformat(t["end_date"]) for t in timeline]
    min_date = min(all_starts)
    max_date = max(all_ends)
    total_span = max((max_date - min_date).days, 1)
    bar_width = 30

    for t in timeline:
        start = Date.fromisoformat(t["start_date"])
        end = Date.fromisoformat(t["end_date"])
        start_offset = int((start - min_date).days / total_span * bar_width)
        end_offset = int((end - min_date).days / total_span * bar_width)
        bar_len = max(1, end_offset - start_offset)

        p_style = _priority_style(t["priority"])
        bar = " " * start_offset + f"[{p_style}]{'=' * bar_len}[/]"

        table.add_row(
            t["sr_id"],
            f"[{p_style}]{t['priority']}[/]",
            t["start_date"],
            t["end_date"],
            str(t["duration_days"]),
            bar,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Multi-standard mapping display
# ---------------------------------------------------------------------------

def print_mapping_table(result: AssessmentResult) -> None:
    """Print cross-standard mapping for all assessed SRs."""
    from iec62443_audit.standards.mapping import get_mapped_standards_for_sr

    console.print("\n[bold cyan]Cross-Standard Compliance Matrix[/]\n")

    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("SR", width=8)
    table.add_column("NIST CSF", min_width=14)
    table.add_column("ISO 27001", min_width=14)
    table.add_column("CIS Controls", min_width=12)
    table.add_column("EU CRA", min_width=18)
    table.add_column("NIS2", min_width=14)

    for fr in result.fr_results:
        for sr in fr.sr_results:
            mappings = get_mapped_standards_for_sr(sr.sr_id)
            nist = ", ".join(mappings.get("NIST Cybersecurity Framework", []))
            iso = ", ".join(mappings.get("ISO/IEC 27001:2022", []))
            cis = ", ".join(mappings.get("CIS Controls v8", []))
            cra = ", ".join(mappings.get("EU Cyber Resilience Act", []))
            nis2 = ", ".join(mappings.get("NIS2 Directive", []))

            table.add_row(
                sr.sr_id,
                nist or "[dim]--[/]",
                iso or "[dim]--[/]",
                cis or "[dim]--[/]",
                cra or "[dim]--[/]",
                nis2 or "[dim]--[/]",
            )

    console.print(table)


# ---------------------------------------------------------------------------
# Maturity display
# ---------------------------------------------------------------------------

def print_maturity_summary(tracker: "MaturityTracker") -> None:
    """Print maturity model summary."""
    from iec62443_audit.maturity import MaturityLevel, MaturityTracker

    counts = tracker.count_by_level()
    total = sum(counts.values()) or 1

    console.print("\n[bold cyan]Implementation Maturity Summary[/]\n")

    for level in MaturityLevel:
        count = counts.get(level, 0)
        pct = count / total * 100
        bar = _compliance_bar(pct, width=25)
        console.print(
            f"  {level.symbol} [{level.color}]{level.label:15}[/] "
            f"{count:3d} {bar}"
        )

    console.print(
        f"\n  Overall Maturity Score: [bold]{tracker.overall_maturity_score:.1f}[/] / 4.0"
    )
    console.print(
        f"  Implemented or above:  [bold]{tracker.implemented_or_above_pct:.0f}%[/]"
    )


# ---------------------------------------------------------------------------
# Zone summary display
# ---------------------------------------------------------------------------

def print_zone_summary(site: "SiteAssessment") -> None:
    """Print multi-zone site assessment summary."""
    from iec62443_audit.zones import SiteAssessment

    console.print()
    console.print(
        Panel.fit(
            f"[bold]Site Assessment: {site.site_name}[/]\n"
            f"Zones: {site.zone_count}  |  "
            f"Overall SL: {site.overall_sl}  |  "
            f"Compliance: {site.overall_compliance_pct:.1f}%",
            border_style="cyan",
        )
    )

    table = Table(
        title="Zone Overview",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Zone", min_width=20)
    table.add_column("Type", width=8)
    table.add_column("Criticality", width=12)
    table.add_column("SL-T", justify="center", width=5)
    table.add_column("SL-A", justify="center", width=14)
    table.add_column("Compliance", width=28)
    table.add_column("Gaps", justify="center", width=5)

    for zs in site.zone_summary():
        badge = _sl_badge(zs["sl_achieved"], zs["sl_target"])
        bar = _compliance_bar(zs["compliance_pct"])
        crit_color = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(zs["criticality"], "white")

        table.add_row(
            zs["name"],
            zs["type"],
            f"[{crit_color}]{zs['criticality']}[/]",
            str(zs["sl_target"]),
            badge,
            bar,
            str(zs["gaps"]),
        )

    console.print(table)


# ---------------------------------------------------------------------------
# CSV / Markdown export helpers
# ---------------------------------------------------------------------------

def export_csv(result: AssessmentResult, path: str) -> None:
    """Export assessment to CSV."""
    import csv
    from pathlib import Path

    with Path(path).open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "FR_ID", "FR_Name", "SR_ID", "SR_Name",
            "SL_Achieved", "SL_Target", "Gap", "Compliant", "Notes",
        ])
        for fr in result.fr_results:
            for sr in fr.sr_results:
                writer.writerow([
                    fr.fr_id, fr.fr_name, sr.sr_id, sr.sr_name,
                    sr.sl_achieved, sr.sl_target, sr.gap,
                    "Yes" if sr.compliant else "No", sr.notes,
                ])

    console.print(f"[green]CSV exported to:[/] {path}")


def export_markdown(result: AssessmentResult, path: str) -> None:
    """Export assessment to Markdown."""
    from pathlib import Path

    lines = [
        f"# IEC 62443 Assessment: {result.system_name}",
        "",
        f"- **Date:** {result.assessment_date}",
        f"- **Assessor:** {result.assessor_name}",
        f"- **Target:** SL-{result.sl_target}",
        f"- **Overall SL:** SL-{result.overall_sl}",
        f"- **Compliance:** {result.overall_compliance_pct:.1f}%",
        f"- **Gaps:** {result.total_gaps}",
        "",
        "## Foundational Requirements",
        "",
        "| FR | Name | SL-A | SL-T | Compliance | Gaps |",
        "|----|------|------|------|------------|------|",
    ]

    for fr in result.fr_results:
        lines.append(
            f"| {fr.fr_id} | {fr.fr_name} ({fr.abbreviation}) | "
            f"{fr.sl_achieved} | {result.sl_target} | "
            f"{fr.compliance_pct:.0f}% | {fr.gap_count} |"
        )

    lines.append("")
    lines.append("## Detailed Results")

    for fr in result.fr_results:
        lines.extend([
            "",
            f"### {fr.fr_id}: {fr.fr_name}",
            "",
            "| SR | Name | SL-A | SL-T | Gap | Notes |",
            "|----|------|------|------|-----|-------|",
        ])
        for sr in fr.sr_results:
            gap_str = f"-{sr.gap}" if sr.gap > 0 else "OK"
            lines.append(
                f"| {sr.sr_id} | {sr.sr_name} | "
                f"{sr.sl_achieved} | {sr.sl_target} | "
                f"{gap_str} | {sr.notes or '--'} |"
            )

    Path(path).write_text("\n".join(lines) + "\n")
    console.print(f"[green]Markdown exported to:[/] {path}")


def import_csv(path: str) -> AssessmentResult:
    """Import an assessment from a CSV file (batch assessment).

    Expected CSV columns:
    SR_ID, SL_Achieved [, Notes]

    Columns are matched against the standard FR/SR database.
    """
    import csv
    from datetime import date
    from pathlib import Path

    from iec62443_audit.requirements import FOUNDATIONAL_REQUIREMENTS

    ratings: Dict[str, tuple] = {}  # sr_id -> (sl_achieved, notes)

    with Path(path).open("r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sr_id = row.get("SR_ID", row.get("sr_id", "")).strip()
            sl = int(row.get("SL_Achieved", row.get("sl_achieved", "0")).strip())
            notes = row.get("Notes", row.get("notes", "")).strip()
            if sr_id:
                ratings[sr_id] = (sl, notes)

    # Build assessment from standard requirements
    from iec62443_audit.scoring import FRResult, SRResult

    result = AssessmentResult(
        system_name="Imported Assessment",
        assessor_name="CSV Import",
        assessment_date=date.today().isoformat(),
        sl_target=2,  # default, can be overridden
    )

    for fr in FOUNDATIONAL_REQUIREMENTS:
        fr_result = FRResult(
            fr_id=fr.id,
            fr_name=fr.name,
            abbreviation=fr.abbreviation,
        )
        for sr in fr.system_requirements:
            sl_achieved, notes = ratings.get(sr.id, (0, "Not assessed"))
            fr_result.sr_results.append(
                SRResult(
                    sr_id=sr.id,
                    sr_name=sr.name,
                    sl_achieved=sl_achieved,
                    sl_target=result.sl_target,
                    notes=notes,
                )
            )
        result.fr_results.append(fr_result)

    return result
