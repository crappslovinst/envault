"""CLI commands for field-level encryption."""

from envault.env_encrypt_field import (
    encrypt_field,
    decrypt_field,
    list_encrypted_fields,
    format_field_list,
    EncryptFieldError,
)


def cmd_encrypt_field(vault: str, password: str, key: str) -> dict:
    """Encrypt a single field in the vault."""
    try:
        result = encrypt_field(vault, password, key)
        result["ok"] = True
        result["formatted"] = f"Field '{key}' encrypted in vault '{vault}'."
        return result
    except EncryptFieldError as e:
        return {"ok": False, "error": str(e)}


def cmd_decrypt_field(vault: str, password: str, key: str) -> dict:
    """Decrypt a single field in the vault."""
    try:
        result = decrypt_field(vault, password, key)
        result["ok"] = True
        result["formatted"] = f"Field '{key}' decrypted in vault '{vault}'."
        return result
    except EncryptFieldError as e:
        return {"ok": False, "error": str(e)}


def cmd_list_encrypted_fields(vault: str, password: str, raw: bool = False) -> dict:
    """List field-encryption status for all keys in a vault."""
    try:
        result = list_encrypted_fields(vault, password)
        result["ok"] = True
        if not raw:
            result["formatted"] = format_field_list(result)
        return result
    except EncryptFieldError as e:
        return {"ok": False, "error": str(e)}
