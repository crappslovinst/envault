"""Flatten nested JSON/dict values in a vault into dot-notation keys."""

from envault.vault_ops import get_env_vars, push_env
import json


class FlattenError(Exception):
    pass


def _flatten_dict(d: dict, prefix: str = "", sep: str = "__") -> dict:
    result = {}
    for k, v in d.items():
        full_key = f"{prefix}{sep}{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_dict(v, full_key, sep))
        else:
            result[full_key.upper()] = str(v)
    return result


def flatten_vault(
    vault_name: str,
    password: str,
    sep: str = "__",
    dry_run: bool = False,
) -> dict:
    env = get_env_vars(vault_name, password)
    if not env:
        raise FlattenError(f"Vault '{vault_name}' is empty or not found.")

    flattened = {}
    changed_keys = []

    for key, value in env.items():
        stripped = value.strip()
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                nested = _flatten_dict(parsed, prefix=key, sep=sep)
                flattened.update(nested)
                changed_keys.append(key)
                continue
        except (json.JSONDecodeError, ValueError):
            pass
        flattened[key] = value

    if not dry_run and changed_keys:
        push_env(vault_name, password, flattened)

    return {
        "vault": vault_name,
        "original_count": len(env),
        "flattened_count": len(flattened),
        "expanded_keys": changed_keys,
        "dry_run": dry_run,
        "env": flattened,
    }


def format_flatten_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Keys before : {result['original_count']}",
        f"Keys after  : {result['flattened_count']}",
        f"Expanded    : {len(result['expanded_keys'])}",
    ]
    if result["expanded_keys"]:
        lines.append("Flattened from: " + ", ".join(result["expanded_keys"]))
    if result["dry_run"]:
        lines.append("[dry-run] No changes written.")
    return "\n".join(lines)
