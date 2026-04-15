"""Validate vault env vars against a set of required keys or rules."""

from typing import Optional
from envault.vault_ops import get_env_vars


class ValidationError(Exception):
    pass


def validate_required(vault: str, password: str, required_keys: list[str]) -> dict:
    """Check that all required_keys exist in the vault. Returns a summary."""
    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise ValidationError(f"Could not load vault '{vault}': {e}") from e

    missing = [k for k in required_keys if k not in env]
    present = [k for k in required_keys if k in env]

    return {
        "vault": vault,
        "required": required_keys,
        "present": present,
        "missing": missing,
        "valid": len(missing) == 0,
    }


def validate_non_empty(vault: str, password: str, keys: Optional[list[str]] = None) -> dict:
    """Check that the given keys (or all keys) have non-empty values."""
    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise ValidationError(f"Could not load vault '{vault}': {e}") from e

    check_keys = keys if keys is not None else list(env.keys())
    empty = [k for k in check_keys if k in env and env[k].strip() == ""]
    not_found = [k for k in check_keys if k not in env]

    return {
        "vault": vault,
        "checked": check_keys,
        "empty_values": empty,
        "not_found": not_found,
        "valid": len(empty) == 0 and len(not_found) == 0,
    }


def validate_pattern(vault: str, password: str, key: str, pattern: str) -> dict:
    """Check that a specific key's value matches a regex pattern."""
    import re

    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise ValidationError(f"Could not load vault '{vault}': {e}") from e

    if key not in env:
        raise ValidationError(f"Key '{key}' not found in vault '{vault}'")

    value = env[key]
    matched = bool(re.search(pattern, value))

    return {
        "vault": vault,
        "key": key,
        "pattern": pattern,
        "value": value,
        "matched": matched,
        "valid": matched,
    }
