"""CLI operations for rotation reminders."""

from __future__ import annotations

from typing import Any

from envault.remind import (
    RemindError,
    set_rotation_reminder,
    get_reminders,
    check_due,
    clear_reminder,
)


def cmd_set_reminder(vault_name: str, key: str, password: str, interval_days: int) -> dict[str, Any]:
    """Set a rotation reminder for a vault key."""
    try:
        result = set_rotation_reminder(vault_name, key, password, interval_days)
        return {"ok": True, **result}
    except RemindError as e:
        return {"ok": False, "error": str(e)}


def cmd_check_reminders(vault_name: str, password: str) -> dict[str, Any]:
    """Check which keys are due for rotation."""
    try:
        due = check_due(vault_name, password)
        return {"ok": True, "vault": vault_name, "due": due, "count": len(due)}
    except RemindError as e:
        return {"ok": False, "error": str(e)}


def cmd_list_reminders(vault_name: str, password: str) -> dict[str, Any]:
    """List all reminders configured for a vault."""
    try:
        reminders = get_reminders(vault_name, password)
        return {"ok": True, "vault": vault_name, "reminders": reminders}
    except RemindError as e:
        return {"ok": False, "error": str(e)}


def cmd_clear_reminder(vault_name: str, key: str, password: str) -> dict[str, Any]:
    """Remove a rotation reminder for a specific key."""
    try:
        result = clear_reminder(vault_name, key, password)
        return {"ok": True, **result}
    except RemindError as e:
        return {"ok": False, "error": str(e)}


def format_due_list(due: list[dict]) -> str:
    """Format a list of due reminders for display."""
    if not due:
        return "All keys are up to date."
    lines = []
    for item in due:
        lines.append(
            f"  [{item['key']}] overdue by {item['elapsed_days'] - item['interval_days']:.1f} days "
            f"(interval: {item['interval_days']}d, elapsed: {item['elapsed_days']}d)"
        )
    return "Keys due for rotation:\n" + "\n".join(lines)
