"""CLI-facing wrappers that format output and handle user-facing errors."""

from pathlib import Path
from typing import Dict, Optional

from envault.vault_ops import push_env, pull_env, get_env_vars
from envault.storage import list_vaults, vault_exists


def cmd_push(
    vault_name: str,
    password: str,
    env_path: Optional[str] = None,
) -> str:
    """Push a .env file into a named vault. Returns a human-readable status string."""
    path = Path(env_path) if env_path else None
    try:
        parsed = push_env(vault_name, password, env_path=path)
        count = len(parsed)
        return f"✓ Pushed {count} variable(s) to vault '{vault_name}'."
    except FileNotFoundError as exc:
        return f"✗ File not found: {exc}"
    except Exception as exc:
        return f"✗ Failed to push: {exc}"


def cmd_pull(
    vault_name: str,
    password: str,
    env_path: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """Pull a vault into a .env file. Returns a human-readable status string."""
    path = Path(env_path) if env_path else None
    try:
        parsed = pull_env(vault_name, password, env_path=path, overwrite=overwrite)
        count = len(parsed)
        dest = path or Path(".env")
        return f"✓ Pulled {count} variable(s) from vault '{vault_name}' → {dest}"
    except FileNotFoundError as exc:
        return f"✗ Vault not found: {exc}"
    except FileExistsError as exc:
        return f"✗ {exc} Use --overwrite to replace it."
    except Exception as exc:
        return f"✗ Failed to pull: {exc}"


def cmd_list() -> str:
    """List all available vaults. Returns a formatted string."""
    vaults = list_vaults()
    if not vaults:
        return "No vaults found."
    lines = ["Available vaults:"]
    for name in sorted(vaults):
        lines.append(f"  • {name}")
    return "\n".join(lines)


def cmd_show(vault_name: str, password: str) -> str:
    """Decrypt and display vault contents as KEY=VALUE lines."""
    if not vault_exists(vault_name):
        return f"✗ Vault '{vault_name}' does not exist."
    try:
        data = get_env_vars(vault_name, password)
        if not data:
            return f"Vault '{vault_name}' is empty."
        lines = [f"Variables in '{vault_name}':"]
        for key, value in sorted(data.items()):
            masked = value[:2] + "*" * max(0, len(value) - 2)
            lines.append(f"  {key}={masked}")
        return "\n".join(lines)
    except Exception as exc:
        return f"✗ Could not decrypt vault: {exc}"
