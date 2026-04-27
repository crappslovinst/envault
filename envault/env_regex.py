"""env_regex.py — regex-based operations on vault keys/values.

Supports:
  - find_by_regex: find keys/values matching a pattern
  - replace_by_regex: replace matches in values using re.sub
  - validate_by_regex: check that values for given keys match a pattern
"""

import re
from typing import Optional

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class RegexError(Exception):
    """Raised for regex operation failures."""


def find_by_regex(
    vault: str,
    password: str,
    pattern: str,
    search_keys: bool = True,
    search_values: bool = True,
    flags: int = re.IGNORECASE,
) -> dict:
    """Return all entries whose key or value matches *pattern*.

    Args:
        vault: vault name.
        password: decryption password.
        pattern: regular expression string.
        search_keys: whether to match against keys.
        search_values: whether to match against values.
        flags: regex flags (default: IGNORECASE).

    Returns:
        Dict with keys 'matches' (list of {key, value}) and 'total'.
    """
    if not vault_exists(vault):
        raise RegexError(f"Vault '{vault}' not found.")

    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise RegexError(f"Invalid regex pattern: {exc}") from exc

    env = get_env_vars(vault, password)
    matches = []

    for key, value in env.items():
        hit = (search_keys and compiled.search(key)) or (
            search_values and compiled.search(value)
        )
        if hit:
            matches.append({"key": key, "value": value})

    return {"vault": vault, "pattern": pattern, "matches": matches, "total": len(matches)}


def replace_by_regex(
    vault: str,
    password: str,
    pattern: str,
    replacement: str,
    keys: Optional[list] = None,
    dry_run: bool = False,
    flags: int = 0,
) -> dict:
    """Replace regex matches inside values and push the updated vault.

    Args:
        vault: vault name.
        password: decryption password.
        pattern: regular expression string.
        replacement: replacement string (supports backreferences).
        keys: optional list of keys to restrict substitution to.
        dry_run: if True, compute changes but do not persist.
        flags: regex flags.

    Returns:
        Dict summarising changed/unchanged counts and affected keys.
    """
    if not vault_exists(vault):
        raise RegexError(f"Vault '{vault}' not found.")

    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise RegexError(f"Invalid regex pattern: {exc}") from exc

    env = get_env_vars(vault, password)
    updated = dict(env)
    changed_keys = []

    for key, value in env.items():
        if keys is not None and key not in keys:
            continue
        new_value = compiled.sub(replacement, value)
        if new_value != value:
            updated[key] = new_value
            changed_keys.append({"key": key, "old": value, "new": new_value})

    if changed_keys and not dry_run:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "pattern": pattern,
        "replacement": replacement,
        "changed": len(changed_keys),
        "unchanged": len(env) - len(changed_keys),
        "dry_run": dry_run,
        "keys": changed_keys,
    }


def validate_by_regex(
    vault: str,
    password: str,
    rules: dict,
    flags: int = 0,
) -> dict:
    """Validate that specific keys match expected patterns.

    Args:
        vault: vault name.
        password: decryption password.
        rules: mapping of key -> regex pattern that the value must satisfy.
        flags: regex flags.

    Returns:
        Dict with 'passed', 'failed' (list of {key, value, pattern}),
        and 'missing' (keys not present in the vault).
    """
    if not vault_exists(vault):
        raise RegexError(f"Vault '{vault}' not found.")

    env = get_env_vars(vault, password)
    passed, failed, missing = [], [], []

    for key, pattern in rules.items():
        if key not in env:
            missing.append(key)
            continue
        try:
            compiled = re.compile(pattern, flags)
        except re.error as exc:
            raise RegexError(f"Invalid pattern for key '{key}': {exc}") from exc

        value = env[key]
        if compiled.fullmatch(value):
            passed.append(key)
        else:
            failed.append({"key": key, "value": value, "pattern": pattern})

    return {
        "vault": vault,
        "passed": passed,
        "failed": failed,
        "missing": missing,
        "ok": len(failed) == 0 and len(missing) == 0,
    }


def format_regex_result(result: dict) -> str:
    """Return a human-readable summary of a regex operation result."""
    op_keys = set(result.keys())

    # find_by_regex result
    if "matches" in op_keys and "total" in op_keys and "changed" not in op_keys:
        lines = [f"Vault : {result['vault']}",
                 f"Pattern: {result['pattern']}",
                 f"Matches: {result['total']}"]
        for m in result["matches"]:
            lines.append(f"  {m['key']} = {m['value']}")
        return "\n".join(lines)

    # replace_by_regex result
    if "changed" in op_keys and "replacement" in op_keys:
        tag = " [dry-run]" if result.get("dry_run") else ""
        lines = [f"Vault    : {result['vault']}{tag}",
                 f"Pattern  : {result['pattern']}",
                 f"Replace  : {result['replacement']}",
                 f"Changed  : {result['changed']}",
                 f"Unchanged: {result['unchanged']}"]
        for entry in result["keys"]:
            lines.append(f"  {entry['key']}: {entry['old']!r} -> {entry['new']!r}")
        return "\n".join(lines)

    # validate_by_regex result
    status = "OK" if result.get("ok") else "FAILED"
    lines = [f"Vault  : {result['vault']}",
             f"Status : {status}",
             f"Passed : {len(result.get('passed', []))}",
             f"Failed : {len(result.get('failed', []))}",
             f"Missing: {len(result.get('missing', []))}"]
    for f in result.get("failed", []):
        lines.append(f"  FAIL  {f['key']} = {f['value']!r} (expected /{f['pattern']}/)") 
    for k in result.get("missing", []):
        lines.append(f"  MISS  {k}")
    return "\n".join(lines)
