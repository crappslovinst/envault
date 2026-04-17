"""Search vault contents by key/value pattern with context."""

import re
from envault.vault_ops import get_env_vars


class GrepError(Exception):
    pass


def grep_vault(vault_name: str, password: str, pattern: str, *, search_keys: bool = True, search_values: bool = True, case_sensitive: bool = False) -> dict:
    """Search for pattern in vault keys and/or values."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise GrepError(str(e)) from e

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        raise GrepError(f"Invalid pattern: {e}") from e

    matches = []
    for key, value in env.items():
        matched_in_key = search_keys and bool(rx.search(key))
        matched_in_value = search_values and bool(rx.search(value))
        if matched_in_key or matched_in_value:
            matches.append({
                "key": key,
                "value": value,
                "matched_key": matched_in_key,
                "matched_value": matched_in_value,
            })

    return {
        "vault": vault_name,
        "pattern": pattern,
        "total_keys": len(env),
        "match_count": len(matches),
        "matches": matches,
    }


def format_grep_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}  pattern={result['pattern']}  matches={result['match_count']}/{result['total_keys']}"]
    for m in result["matches"]:
        tag = "[K+V]" if m["matched_key"] and m["matched_value"] else ("[KEY]" if m["matched_key"] else "[VAL]")
        lines.append(f"  {tag}  {m['key']}={m['value']}")
    return "\n".join(lines)
