"""CLI commands for vault archiving."""

from envault.env_archive import archive_vault, unarchive_vault, list_archived, ArchiveError
from envault.storage import list_vaults


def cmd_archive(name: str, password: str) -> dict:
    """Archive a vault."""
    try:
        return archive_vault(name, password)
    except ArchiveError as e:
        return {"status": "error", "message": str(e)}


def cmd_unarchive(name: str, password: str, new_name: str | None = None) -> dict:
    """Restore an archived vault."""
    try:
        return unarchive_vault(name, password, new_name)
    except ArchiveError as e:
        return {"status": "error", "message": str(e)}


def cmd_list_archived() -> dict:
    """List all archived vaults."""
    try:
        all_vaults = list_vaults()
        archived = list_archived(all_vaults)
        return {"status": "ok", "archived": archived, "count": len(archived)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def format_archive_list(result: dict) -> str:
    if result.get("status") == "error":
        return f"Error: {result['message']}"
    archived = result.get("archived", [])
    if not archived:
        return "No archived vaults."
    lines = [f"Archived vaults ({result['count']}):"] + [f"  - {v}" for v in archived]
    return "\n".join(lines)
