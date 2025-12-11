"""Command-line interface for iec62443-audit.

Subcommands:
    assess   -- Run an interactive IEC 62443 assessment
    report   -- Generate reports from a saved assessment JSON
    compare  -- Compare two assessments for progress tracking
    matrix   -- Export full compliance matrix (cross-standard mapping)
    zones    -- Multi-zone site assessment management

Global flags:
    --tui          Launch interactive Textual TUI (requires textual)
    --zone NAME    Specify zone for multi-zone assessments
    --standard     Select standard: iec62443-3-3 or iec62443-4-2
    --format       Output format: table, json, html, csv, markdown
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from iec62443_audit import __version__


def _cmd_assess(args: argparse.Namespace) -> None:
    from iec62443_audit.assessor import InteractiveAssessor
    from iec62443_audit.display import (
        print_fr_table,
        print_gap_heatmap,
        print_spider_chart,
        print_stats_cards,
        print_header,
        export_csv,
        export_markdown,
    )
    from iec62443_audit.report import (
        export_html,
        export_json,
        print_gaps,
        print_summary,
    )

    assessor = InteractiveAssessor(
        sl_target=args.target,
        standard=args.standard,
    )
    result = assessor.run()

    # Rich console output
    print_header(result)
    print_stats_cards(result)
    print_fr_table(result)
    print_spider_chart(result)
    print_gap_heatmap(result)
    print_gaps(result)

    # Save files
    json_path = Path(args.output).with_suffix(".json")
    export_json(result, json_path)

    fmt = getattr(args, "format", "html")
    if fmt == "csv":
        csv_path = Path(args.output).with_suffix(".csv")
        export_csv(result, str(csv_path))
    elif fmt == "markdown":
        md_path = Path(args.output).with_suffix(".md")
        export_markdown(result, str(md_path))
    else:
        if args.html:
            html_path = Path(args.html)
        else:
            html_path = Path(args.output).with_suffix(".html")
        export_html(result, html_path)

    # Generate action plan if requested
    if getattr(args, "action_plan", False):
        from iec62443_audit.action_plan import generate_action_plan, generate_timeline
        from iec62443_audit.display import print_action_plan, print_timeline

        plan = generate_action_plan(result)
        print_action_plan(plan)
        timeline = generate_timeline(plan)
        print_timeline(timeline)


def _cmd_report(args: argparse.Namespace) -> None:
    from iec62443_audit.display import (
        print_fr_table,
        print_gap_heatmap,
        print_spider_chart,
        print_stats_cards,
        print_header,
        print_mapping_table,
        export_csv,
        export_markdown,
    )
    from iec62443_audit.report import (
        export_html,
        load_json,
        print_gaps,
        print_summary,
    )

    result = load_json(Path(args.input))

    # Rich output
    print_header(result)
    print_stats_cards(result)
    print_fr_table(result)

    if args.spider:
        print_spider_chart(result)

    if args.heatmap:
        print_gap_heatmap(result)

    if args.gaps:
        print_gaps(result)

    if args.mapping:
        print_mapping_table(result)

    # Export formats
    fmt = getattr(args, "format", None)
    if fmt == "csv":
        csv_path = Path(args.input).with_suffix(".csv")
        export_csv(result, str(csv_path))
    elif fmt == "markdown":
        md_path = Path(args.input).with_suffix(".md")
        export_markdown(result, str(md_path))
    elif args.html:
        export_html(result, Path(args.html))

    # Action plan
    if getattr(args, "action_plan", False):
        from iec62443_audit.action_plan import generate_action_plan, generate_timeline
        from iec62443_audit.display import print_action_plan, print_timeline

        plan = generate_action_plan(result)
        print_action_plan(plan)
        timeline = generate_timeline(plan)
        print_timeline(timeline)


def _cmd_compare(args: argparse.Namespace) -> None:
    from iec62443_audit.display import print_side_by_side
    from iec62443_audit.report import load_json

    baseline = load_json(Path(args.baseline))
    current = load_json(Path(args.current))
    print_side_by_side(baseline, current)


def _cmd_matrix(args: argparse.Namespace) -> None:
    from iec62443_audit.display import print_mapping_table
    from iec62443_audit.report import load_json

    if args.input:
        result = load_json(Path(args.input))
    else:
        # Show full matrix for all SRs
        from iec62443_audit.requirements import FOUNDATIONAL_REQUIREMENTS
        from iec62443_audit.scoring import AssessmentResult, FRResult, SRResult

        result = AssessmentResult(
            system_name="Full Standard",
            assessor_name="Reference",
            assessment_date="",
            sl_target=2,
        )
        for fr in FOUNDATIONAL_REQUIREMENTS:
            fr_result = FRResult(
                fr_id=fr.id, fr_name=fr.name, abbreviation=fr.abbreviation
            )
            for sr in fr.system_requirements:
                fr_result.sr_results.append(
                    SRResult(
                        sr_id=sr.id,
                        sr_name=sr.name,
                        sl_achieved=0,
                        sl_target=2,
                    )
                )
            result.fr_results.append(fr_result)

    print_mapping_table(result)


def _cmd_import(args: argparse.Namespace) -> None:
    from iec62443_audit.display import import_csv, print_fr_table, print_stats_cards, print_header
    from iec62443_audit.report import export_json, export_html

    result = import_csv(args.input)

    if args.target:
        result.sl_target = args.target
        for fr in result.fr_results:
            for sr in fr.sr_results:
                sr.sl_target = args.target

    if args.name:
        result.system_name = args.name

    print_header(result)
    print_stats_cards(result)
    print_fr_table(result)

    out_path = Path(args.output) if args.output else Path(args.input).with_suffix(".json")
    export_json(result, out_path)
    export_html(result, out_path.with_suffix(".html"))


def _cmd_tui(args: argparse.Namespace) -> None:
    from iec62443_audit.tui import launch_tui

    try:
        launch_tui(
            sl_target=getattr(args, "target", 2),
            system_name=getattr(args, "system_name", ""),
            assessor_name=getattr(args, "assessor_name", ""),
            standard=getattr(args, "standard", "iec62443-3-3"),
            load_file=getattr(args, "load", None),
        )
    except ImportError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iec62443-audit",
        description=(
            "IEC 62443 security level assessment tool for industrial "
            "control systems. Evaluate SL-Achieved against SL-Target with "
            "interactive checklists, gap analysis, action plans, "
            "cross-standard mapping, and multi-zone support."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        default=False,
        help="Launch interactive Textual TUI (requires: pip install iec62443-audit[tui])",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── assess ────────────────────────────────────────────────────────
    p_assess = sub.add_parser(
        "assess",
        help="Run an interactive IEC 62443 assessment",
    )
    p_assess.add_argument(
        "-t",
        "--target",
        type=int,
        choices=[1, 2, 3, 4],
        default=2,
        help="Target Security Level (default: 2)",
    )
    p_assess.add_argument(
        "-o",
        "--output",
        default="assessment",
        help="Output file base name (default: assessment)",
    )
    p_assess.add_argument(
        "--html",
        default=None,
        help="HTML output file path (default: <output>.html)",
    )
    p_assess.add_argument(
        "--standard",
        choices=["iec62443-3-3", "iec62443-4-2"],
        default="iec62443-3-3",
        help="Standard to assess against (default: iec62443-3-3)",
    )
    p_assess.add_argument(
        "--zone",
        default=None,
        help="Zone name for multi-zone assessments",
    )
    p_assess.add_argument(
        "--format",
        choices=["table", "json", "html", "csv", "markdown"],
        default="html",
        help="Output format (default: html)",
    )
    p_assess.add_argument(
        "--action-plan",
        action="store_true",
        default=False,
        help="Generate remediation action plan after assessment",
    )
    p_assess.set_defaults(func=_cmd_assess)

    # ── report ────────────────────────────────────────────────────────
    p_report = sub.add_parser(
        "report",
        help="Generate reports from a saved assessment JSON",
    )
    p_report.add_argument(
        "input",
        help="Path to assessment JSON file",
    )
    p_report.add_argument(
        "--html",
        default=None,
        help="Generate HTML report at the given path",
    )
    p_report.add_argument(
        "--gaps",
        action="store_true",
        default=False,
        help="Show gap analysis table",
    )
    p_report.add_argument(
        "--spider",
        action="store_true",
        default=False,
        help="Show spider/radar chart of SL per FR",
    )
    p_report.add_argument(
        "--heatmap",
        action="store_true",
        default=False,
        help="Show gap analysis heatmap",
    )
    p_report.add_argument(
        "--mapping",
        action="store_true",
        default=False,
        help="Show cross-standard compliance mapping",
    )
    p_report.add_argument(
        "--action-plan",
        action="store_true",
        default=False,
        help="Generate remediation action plan",
    )
    p_report.add_argument(
        "--format",
        choices=["table", "json", "html", "csv", "markdown"],
        default=None,
        help="Export format (csv, markdown, etc.)",
    )
    p_report.set_defaults(func=_cmd_report)

    # ── compare ───────────────────────────────────────────────────────
    p_compare = sub.add_parser(
        "compare",
        help="Compare two assessments for progress tracking",
    )
    p_compare.add_argument(
        "baseline",
        help="Path to baseline assessment JSON",
    )
    p_compare.add_argument(
        "current",
        help="Path to current assessment JSON",
    )
    p_compare.set_defaults(func=_cmd_compare)

    # ── matrix ────────────────────────────────────────────────────────
    p_matrix = sub.add_parser(
        "matrix",
        help="Export full compliance matrix (cross-standard mapping)",
    )
    p_matrix.add_argument(
        "--input",
        default=None,
        help="Assessment JSON to map (omit for full standard reference)",
    )
    p_matrix.set_defaults(func=_cmd_matrix)

    # ── import ────────────────────────────────────────────────────────
    p_import = sub.add_parser(
        "import",
        help="Import assessment from CSV (batch assessment)",
    )
    p_import.add_argument(
        "input",
        help="Path to CSV file with SR_ID,SL_Achieved[,Notes] columns",
    )
    p_import.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output JSON path (default: <input>.json)",
    )
    p_import.add_argument(
        "-t",
        "--target",
        type=int,
        choices=[1, 2, 3, 4],
        default=None,
        help="Override target SL",
    )
    p_import.add_argument(
        "-n",
        "--name",
        default=None,
        help="System name override",
    )
    p_import.set_defaults(func=_cmd_import)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle --tui flag (works with or without a subcommand)
    if args.tui:
        _cmd_tui(args)
        return

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
