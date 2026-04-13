"""CLI commands for viewing the envault audit log."""

from typing import Optional

from envault.audit import get_events, clear_events


def cmd_log(
    vault_name: Optional[str] = None,
    limit: int = 20,
    vault_dir: Optional[str] = None,
) -> list[dict]:
    """Return recent audit events, optionally filtered by vault.

    Args:
        vault_name: If provided, only return events for this vault.
        limit: Maximum number of events to return (most recent first).
        vault_dir: Override default vault directory (for testing).

    Returns:
        List of event dicts.
    """
    events = get_events(vault_name=vault_name, vault_dir=vault_dir)
    return events[-limit:][::-1]


def cmd_clear_log(vault_dir: Optional[str] = None) -> str:
    """Clear the entire audit log.

    Args:
        vault_dir: Override default vault directory (for testing).

    Returns:
        Confirmation message.
    """
    clear_events(vault_dir=vault_dir)
    return "Audit log cleared."


def format_event(event: dict) -> str:
    """Format a single audit event for display."""
    ts = event.get("timestamp", "unknown")
    action = event.get("action", "?")
    vault = event.get("vault", "?")
    user = event.get("user", "?")
    extra = event.get("extra", {})
    line = f"[{ts}] {action.upper():6s} vault={vault!r} user={user!r}"
    if extra:
        kv = " ".join(f"{k}={v}" for k, v in extra.items())
        line += f" ({kv})"
    return line
