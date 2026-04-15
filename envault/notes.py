"""Vault notes — attach freeform text notes to a vault."""

from datetime import datetime, timezone
from envault.storage import load_vault, save_vault, vault_exists


class NoteError(Exception):
    pass


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_notes(vault: dict) -> list:
    return vault.get("__notes__", [])


def add_note(vault_name: str, password: str, text: str) -> dict:
    """Append a timestamped note to the vault."""
    if not vault_exists(vault_name):
        raise NoteError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    notes = _get_notes(vault)
    entry = {"ts": _ts(), "text": text}
    notes.append(entry)
    vault["__notes__"] = notes
    save_vault(vault_name, vault, password)
    return entry


def get_notes(vault_name: str, password: str) -> list:
    """Return all notes attached to the vault."""
    if not vault_exists(vault_name):
        raise NoteError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    return _get_notes(vault)


def delete_note(vault_name: str, password: str, index: int) -> dict:
    """Delete a note by zero-based index. Returns the removed entry."""
    if not vault_exists(vault_name):
        raise NoteError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    notes = _get_notes(vault)
    if index < 0 or index >= len(notes):
        raise NoteError(f"Note index {index} out of range (vault has {len(notes)} note(s)).")
    removed = notes.pop(index)
    vault["__notes__"] = notes
    save_vault(vault_name, vault, password)
    return removed


def clear_notes(vault_name: str, password: str) -> int:
    """Remove all notes from the vault. Returns count deleted."""
    if not vault_exists(vault_name):
        raise NoteError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    count = len(_get_notes(vault))
    vault["__notes__"] = []
    save_vault(vault_name, vault, password)
    return count
