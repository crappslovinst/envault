"""Local encrypted storage for envault vault files."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt


DEFAULT_VAULT_DIR = Path.home() / ".envault" / "vaults"


def _vault_path(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    return vault_dir / f"{vault_name}.vault"


def save_vault(vault_name: str, data: dict, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    """Encrypt and save vault data to disk."""
    vault_dir.mkdir(parents=True, exist_ok=True)
    path = _vault_path(vault_name, vault_dir)
    plaintext = json.dumps(data)
    encrypted = encrypt(plaintext, password)
    path.write_text(encrypted, encoding="utf-8")
    return path


def load_vault(vault_name: str, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> dict:
    """Load and decrypt vault data from disk."""
    path = _vault_path(vault_name, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' not found at {path}.")
    encrypted = path.read_text(encoding="utf-8")
    plaintext = decrypt(encrypted, password)
    return json.loads(plaintext)


def vault_exists(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    """Check whether a vault file exists on disk."""
    return _vault_path(vault_name, vault_dir).exists()


def list_vaults(vault_dir: Path = DEFAULT_VAULT_DIR) -> list[str]:
    """Return names of all stored vaults."""
    if not vault_dir.exists():
        return []
    return [p.stem for p in vault_dir.glob("*.vault")]


def delete_vault(vault_name: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Delete a vault file from disk."""
    path = _vault_path(vault_name, vault_dir)
    if not path.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' not found.")
    path.unlink()
