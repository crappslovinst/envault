from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class DiffKeysError(Exception):
    pass


def diff_keys(vault_a: str, password_a: str, vault_b: str, password_b: str) -> dict:
    """Compare keys between two vaults without comparing values."""
    if not vault_exists(vault_a):
        raise DiffKeysError(f"Vault not found: {vault_a}")
    if not vault_exists(vault_b):
        raise DiffKeysError(f"Vault not found: {vault_b}")

    env_a = get_env_vars(vault_a, password_a)
    env_b = get_env_vars(vault_b, password_b)

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
        f"Key diff: {result['vault_a']} vs {result['vault_b']}",
        f"  Shared keys   : {result['shared']}",
        f"  Only in {result['vault_a']}: {result['unique_to_a']}",
        f"  Only in {result['vault_b']}: {result['unique_to_b']}",
    ]
    if result["only_in_a"]:
        lines.append(f"  Keys only in {result['vault_a']}:")
        for k in result["only_in_a"]:
            lines.append(f"    - {k}")
    if result["only_in_b"]:
        lines.append(f"  Keys only in {result['vault_b']}:")
        for k in result["only_in_b"]:
            lines.append(f"    + {k}")
    return "\n".join(lines)
