"""Textual TUI for iec62443-audit.

Optional dependency: install with `pip install iec62443-audit[tui]`.
"""

from __future__ import annotations


def check_textual_available() -> bool:
    """Check if textual is installed."""
    try:
        import textual  # noqa: F401
        return True
    except ImportError:
        return False


def launch_tui(**kwargs) -> None:
    """Launch the Textual TUI application.

    Raises ImportError with a helpful message if textual is not installed.
    """
    if not check_textual_available():
        raise ImportError(
            "Textual is required for the TUI mode.\n"
            "Install with: pip install iec62443-audit[tui]"
        )

    from iec62443_audit.tui.app import AuditApp
    app = AuditApp(**kwargs)
    app.run()
