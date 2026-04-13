"""Audit log for tracking vault operations (push, pull, etc.)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILE = ".envault_audit.json"


def _audit_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    return base / AUDIT_FILE


def record_event(
    action: str,
    vault_name: str,
    user: Optional[str] = None,
    extra: Optional[dict] = None,
    vault_dir: Optional[str] = None,
) -> dict:
    """Append an audit event and return the event dict."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "vault": vault_name,
        "user": user or os.environ.get("USER", "unknown"),
        "extra": extra or {},
    }
    path = _audit_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    events = _load_events(path)
    events.append(event)

    with open(path, "w") as f:
        json.dump(events, f, indent=2)

    return event


def _load_events(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_events(
    vault_name: Optional[str] = None,
    vault_dir: Optional[str] = None,
) -> list:
    """Return audit events, optionally filtered by vault name."""
    events = _load_events(_audit_path(vault_dir))
    if vault_name:
        events = [e for e in events if e.get("vault") == vault_name]
    return events


def clear_events(vault_dir: Optional[str] = None) -> None:
    """Clear all audit events (useful for testing)."""
    path = _audit_path(vault_dir)
    if path.exists():
        path.unlink()
