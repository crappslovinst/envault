"""Archive and unarchive vaults (soft-delete with recovery)."""

from envault.storage import load_vault, save_vault, vault_exists, delete_vault
from envault.audit import record_event


class ArchiveError(Exception):
    pass


ARCHIVE_PREFIX = "__archived__"


def archive_vault(name: str, password: str) -> dict:
    """Soft-delete a vault by renaming it with an archive prefix."""
    if not vault_exists(name):
        raise ArchiveError(f"Vault '{name}' not found")
    archived_name = f"{ARCHIVE_PREFIX}{name}"
    if vault_exists(archived_name):
        raise ArchiveError(f"Vault '{name}' is already archived")
    data = load_vault(name, password)
    save_vault(archived_name, data, password)
    delete_vault(name)
    record_event(archived_name, "archive", {"original": name})
    return {"status": "archived", "vault": name, "archived_as": archived_name}


def unarchive_vault(name: str, password: str, new_name: str | None = None) -> dict:
    """Restore an archived vault, optionally under a new name."""
    archived_name = f"{ARCHIVE_PREFIX}{name}"
    if not vault_exists(archived_name):
        raise ArchiveError(f"No archive found for vault '{name}'")
    target = new_name or name
    if vault_exists(target):
        raise ArchiveError(f"Vault '{target}' already exists; choose a different name")
    data = load_vault(archived_name, password)
    save_vault(target, data, password)
    delete_vault(archived_name)
    record_event(target, "unarchive", {"restored_from": archived_name})
    return {"status": "unarchived", "vault": target}


def list_archived(all_vaults: list[str]) -> list[str]:
    """Filter a vault name list to only archived entries, returning clean names."""
    return [
        v[len(ARCHIVE_PREFIX):]
        for v in all_vaults
        if v.startswith(ARCHIVE_PREFIX)
    ]
