"""env_diff_keys.py — compare key sets between two vaults without revealing values."""

from envault.vault_ops import get_env_vars


class DiffKeysError(Exception):
    pass


def diff_keys(vault_a: str, password_a: str, vault_b: str, password_b: str) -> dict:
    """Return a structured diff of key sets between two vaults."""
    try:
        env_a = get_env_vars(vault_a, password_a)
    except Exception as e:
        raise DiffKeysError(f"Cannot read vault '{vault_a}': {e}")

    try:
        env_b = get_env_vars(vault_b, password_b)
    except Exception as e:
        raise DiffKeysError(f"Cannot read vault '{vault_b}': {e}")

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())

    only_in_a = sorted(keys_a - keys_b)
    only_in_b = sorted(keys_b - keys_a)
    in_both = sorted(keys_a & keys_b)

    return {
        "vault_a": vault_a,
        "vault_b": vault_b,
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "in_both": in_both,
        "total_a": len(keys_a),
        "total_b": len(keys_b),
        "shared": len(in_both),
        "unique_to_a": len(only_in_a),
        "unique_to_b": len(only_in_b),
    }


def format_diff_keys_result(result: dict) -> str:
    lines = [
        f"Key diff: '{result['vault_a']}' vs '{result['vault_b']}'",
        f"  Shared keys   : {result['shared']}",
        f"  Only in A     : {result['unique_to_a']}",
        f"  Only in B     : {result['unique_to_b']}",
    ]
    if result["only_in_a"]:
        lines.append("  Keys only in A: " + ", ".join(result["only_in_a"]))
    if result["only_in_b"]:
        lines.append("  Keys only in B: " + ", ".join(result["only_in_b"]))
    return "\n".join(lines)
