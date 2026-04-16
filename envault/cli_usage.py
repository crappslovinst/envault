"""CLI operations for env usage tracking."""

from envault.env_usage import UsageError, record_access, get_usage, get_most_accessed, clear_usage


def format_usage_entry(entry: dict) -> str:
    """Format a single usage entry for display."""
    key = entry["key"]
    count = entry["count"]
    last = entry.get("last_accessed", "never")
    return f"  {key:<30} accesses={count}  last={last}"


def cmd_record_access(vault: str, key: str, password: str) -> dict:
    """Record an access event for a vault key."""
    try:
        entry = record_access(vault, key, password)
        return {
            "ok": True,
            "vault": vault,
            "key": key,
            "count": entry["count"],
            "last_accessed": entry["last_accessed"],
        }
    except UsageError as e:
        return {"ok": False, "error": str(e)}


def cmd_get_usage(vault: str, password: str, key: str = None) -> dict:
    """Return usage stats for a vault, optionally filtered by key."""
    try:
        entries = get_usage(vault, password, key=key)
        formatted = [format_usage_entry(e) for e in entries]
        return {
            "ok": True,
            "vault": vault,
            "entries": entries,
            "formatted": "\n".join(formatted) if formatted else "  (no usage recorded)",
        }
    except UsageError as e:
        return {"ok": False, "error": str(e)}


def cmd_most_accessed(vault: str, password: str, limit: int = 5) -> dict:
    """Return the most frequently accessed keys in a vault."""
    try:
        entries = get_most_accessed(vault, password, limit=limit)
        formatted = [format_usage_entry(e) for e in entries]
        return {
            "ok": True,
            "vault": vault,
            "limit": limit,
            "entries": entries,
            "formatted": "\n".join(formatted) if formatted else "  (no usage recorded)",
        }
    except UsageError as e:
        return {"ok": False, "error": str(e)}


def cmd_clear_usage(vault: str, password: str) -> dict:
    """Clear all usage data for a vault."""
    try:
        clear_usage(vault, password)
        return {"ok": True, "vault": vault, "message": f"Usage data cleared for '{vault}'."}
    except UsageError as e:
        return {"ok": False, "error": str(e)}
