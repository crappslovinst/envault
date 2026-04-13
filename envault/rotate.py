"""Key rotation support for envault vaults."""

from envault.storage import load_vault, save_vault, vault_exists
from envault.crypto import encrypt, decrypt


class VaultNotFoundError(Exception):
    pass


class RotationError(Exception):
    pass


def rotate_key(vault_name: str, old_password: str, new_password: str) -> dict:
    """Re-encrypt a vault with a new password.

    Loads the vault using the old password, then re-encrypts all values
    with the new password and saves the vault back to disk.

    Returns a summary dict with vault name and number of keys rotated.
    """
    if not vault_exists(vault_name):
        raise VaultNotFoundError(f"Vault '{vault_name}' does not exist.")

    try:
        data = load_vault(vault_name, old_password)
    except Exception as exc:
        raise RotationError(f"Failed to decrypt vault with old password: {exc}") from exc

    if not isinstance(data, dict):
        raise RotationError("Vault data is malformed; expected a dict of env vars.")

    try:
        save_vault(vault_name, data, new_password)
    except Exception as exc:
        raise RotationError(f"Failed to re-encrypt vault with new password: {exc}") from exc

    return {
        "vault": vault_name,
        "keys_rotated": len(data),
    }


def rotate_key_dry_run(vault_name: str, old_password: str) -> dict:
    """Verify the old password is valid and return vault metadata without saving.

    Useful for confirming the old password before committing to a rotation.
    Returns a dict with vault name and key count.
    """
    if not vault_exists(vault_name):
        raise VaultNotFoundError(f"Vault '{vault_name}' does not exist.")

    try:
        data = load_vault(vault_name, old_password)
    except Exception as exc:
        raise RotationError(f"Old password is invalid: {exc}") from exc

    return {
        "vault": vault_name,
        "keys_found": len(data),
        "dry_run": True,
    }
