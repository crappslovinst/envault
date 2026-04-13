"""High-level vault operations: push env data into a vault and pull it back out."""

from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt
from envault.env_parser import parse_env, serialize_env
from envault.storage import save_vault, load_vault, vault_exists


def push_env(
    vault_name: str,
    password: str,
    env_path: Optional[Path] = None,
    env_content: Optional[str] = None,
) -> Dict[str, str]:
    """Read a .env file (or raw content), encrypt it, and save to the vault.

    Returns the parsed key/value pairs that were stored.
    """
    if env_content is None:
        if env_path is None:
            env_path = Path(".env")
        env_content = env_path.read_text(encoding="utf-8")

    parsed = parse_env(env_content)
    serialized = serialize_env(parsed)
    token = encrypt(serialized, password)
    save_vault(vault_name, {"data": token})
    return parsed


def pull_env(
    vault_name: str,
    password: str,
    env_path: Optional[Path] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Decrypt vault contents and write them to a .env file.

    Returns the parsed key/value pairs that were written.
    Raises FileExistsError if the target file exists and overwrite=False.
    """
    if not vault_exists(vault_name):
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")

    vault_data = load_vault(vault_name)
    token = vault_data["data"]
    plaintext = decrypt(token, password)
    parsed = parse_env(plaintext)

    if env_path is None:
        env_path = Path(".env")

    if env_path.exists() and not overwrite:
        raise FileExistsError(
            f"{env_path} already exists. Use overwrite=True to replace it."
        )

    env_path.write_text(serialize_env(parsed), encoding="utf-8")
    return parsed


def get_env_vars(vault_name: str, password: str) -> Dict[str, str]:
    """Decrypt a vault and return its key/value pairs without writing to disk."""
    if not vault_exists(vault_name):
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")

    vault_data = load_vault(vault_name)
    token = vault_data["data"]
    plaintext = decrypt(token, password)
    return parse_env(plaintext)
