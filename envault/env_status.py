"""Vault status overview: combines health, TTL, lock, and tag info."""

from envault.storage import vault_exists
from envault.ttl import get_ttl, is_expired
from envault.lock import is_locked
from envault.tags import get_tags
from envault.audit import get_events


class StatusError(Exception):
    pass


def get_status(vault_name: str, password: str) -> dict:
    """Return a status summary dict for a vault."""
    if not vault_exists(vault_name):
        raise StatusError(f"Vault '{vault_name}' does not exist.")

    ttl_info = get_ttl(vault_name)
    expired = is_expired(vault_name) if ttl_info else False
    locked = is_locked(vault_name)
    tags = get_tags(vault_name, password)

    events = get_events(vault_name)
    last_event = events[-1] if events else None

    return {
        "vault": vault_name,
        "locked": locked,
        "expired": expired,
        "ttl": ttl_info,
        "tags": tags,
        "last_event": last_event,
        "event_count": len(events),
    }


def format_status(status: dict) -> str:
    """Format a status dict into a human-readable string."""
    lines = [
        f"Vault   : {status['vault']}",
        f"Locked  : {'yes' if status['locked'] else 'no'}",
        f"Expired : {'yes' if status['expired'] else 'no'}",
    ]

    ttl = status.get("ttl")
    if ttl:
        lines.append(f"TTL     : expires at {ttl.get('expires_at', 'unknown')}")
    else:
        lines.append("TTL     : none")

    tags = status.get("tags", [])
    lines.append(f"Tags    : {', '.join(tags) if tags else 'none'}")

    last = status.get("last_event")
    if last:
        lines.append(f"Last op : {last.get('action', '?')} at {last.get('timestamp', '?')}")
    else:
        lines.append("Last op : none recorded")

    lines.append(f"Events  : {status['event_count']} total")
    return "\n".join(lines)
