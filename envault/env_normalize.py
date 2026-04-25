"""Normalize .env values: trim whitespace, fix quoting, standardize booleans."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class NormalizeError(Exception):
    pass


_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


def _normalize_value(value: str, normalize_bools: bool = True) -> str:
    value = value.strip()
    if normalize_bools:
        lower = value.lower()
        if lower in _BOOL_TRUE:
            return "true"
        if lower in _BOOL_FALSE:
            return "false"
    return value


def normalize_vault(
    vault_name: str,
    password: str,
    normalize_bools: bool = True,
    dry_run: bool = False,
) -> dict:
    if not vault_exists(vault_name):
        raise NormalizeError(f"Vault '{vault_name}' not found.")

    original = get_env_vars(vault_name, password)
    normalized = {
        k: _normalize_value(v, normalize_bools=normalize_bools)
        for k, v in original.items()
    }

    changed_keys = [k for k in original if original[k] != normalized[k]]

    if changed_keys and not dry_run:
        push_env(vault_name, password, normalized)

    return {
        "vault": vault_name,
        "total": len(original),
        "changed": len(changed_keys),
        "changed_keys": changed_keys,
        "dry_run": dry_run,
    }


def format_normalize_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total : {result['total']}",
        f"Changed: {result['changed']}",
    ]
    if result["changed_keys"]:
        lines.append("Keys  : " + ", ".join(result["changed_keys"]))
    if result["dry_run"]:
        lines.append("(dry run — no changes written)")
    return "\n".join(lines)
