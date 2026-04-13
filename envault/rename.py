"""Rename a vault, updating audit log and preserving all data."""

from envault.storage import load_vault, save_vault, vault_exists, _vault_path
from envault.audit import record_event
import os


class RenameError(Exception):
    pass


def rename_vault(src: str, dst: str, password: str) -> dict:
    """Rename vault `src` to `dst` using `password` to re-encrypt.

    Args:
        src: Name of the existing vault.
        dst: Desired new name for the vault.
        password: Password used to decrypt the source vault.

    Returns:
        A summary dict with keys 'src', 'dst', and 'keys_moved'.

    Raises:
        RenameError: If src doesn't exist, dst already exists, or
                     the password is incorrect.
    """
    if not vault_exists(src):
        raise RenameError(f"Vault '{src}' does not exist.")

    if vault_exists(dst):
        raise RenameError(f"Vault '{dst}' already exists. Delete it first.")

    try:
        data = load_vault(src, password)
    except Exception as exc:
        raise RenameError(f"Could not load vault '{src}': {exc}") from exc

    try:
        save_vault(dst, data, password)
    except Exception as exc:
        raise RenameError(f"Could not save vault '{dst}': {exc}") from exc

    # Remove old vault file
    old_path = _vault_path(src)
    try:
        os.remove(old_path)
    except OSError as exc:
        # Rollback: remove the newly created dst vault
        try:
            os.remove(_vault_path(dst))
        except OSError:
            pass
        raise RenameError(f"Could not remove old vault '{src}': {exc}") from exc

    record_event("rename", dst, {"src": src, "dst": dst})

    return {"src": src, "dst": dst, "keys_moved": len(data)}
