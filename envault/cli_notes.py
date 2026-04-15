"""CLI commands for vault notes."""

from envault.notes import add_note, get_notes, delete_note, clear_notes, NoteError


def format_note(index: int, entry: dict) -> str:
    return f"[{index}] {entry['ts']}\n    {entry['text']}"


def cmd_add_note(vault_name: str, password: str, text: str) -> dict:
    """Add a note and return a status dict."""
    entry = add_note(vault_name, password, text)
    return {"status": "ok", "vault": vault_name, "note": entry}


def cmd_list_notes(vault_name: str, password: str) -> dict:
    """List all notes for a vault."""
    notes = get_notes(vault_name, password)
    formatted = [format_note(i, n) for i, n in enumerate(notes)]
    return {
        "status": "ok",
        "vault": vault_name,
        "count": len(notes),
        "notes": notes,
        "formatted": "\n".join(formatted) if formatted else "(no notes)",
    }


def cmd_delete_note(vault_name: str, password: str, index: int) -> dict:
    """Delete a note by index."""
    removed = delete_note(vault_name, password, index)
    return {"status": "ok", "vault": vault_name, "deleted": removed}


def cmd_clear_notes(vault_name: str, password: str) -> dict:
    """Clear all notes from a vault."""
    count = clear_notes(vault_name, password)
    return {"status": "ok", "vault": vault_name, "cleared": count}
