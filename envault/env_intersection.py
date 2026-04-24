"""env_intersection.py — find keys common to two or more vaults."""

from typing import Optional
from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class IntersectionError(Exception):
    pass


def intersect_vaults(
    vault_names: list[str],
    password: str,
    values_must_match: bool = False,
) -> dict:
    """Return keys (and optionally values) present in ALL listed vaults.

    Args:
        vault_names: Two or more vault names to compare.
        password: Shared decryption password.
        values_must_match: When True, only include keys whose values are
            identical across every vault.

    Returns:
        dict with keys:
            - common_keys: list of keys present in all vaults
            - common_pairs: dict of key→value for keys whose values match
              (populated only when values_must_match=True)
            - vault_count: number of vaults compared
            - total_common: int
    """
    if len(vault_names) < 2:
        raise IntersectionError("At least two vault names are required.")

    for name in vault_names:
        if not vault_exists(name):
            raise IntersectionError(f"Vault not found: {name!r}")

    envs: list[dict] = []
    for name in vault_names:
        try:
            envs.append(get_env_vars(name, password))
        except Exception as exc:
            raise IntersectionError(f"Failed to load vault {name!r}: {exc}") from exc

    common_keys = set(envs[0].keys())
    for env in envs[1:]:
        common_keys &= set(env.keys())

    common_keys_sorted = sorted(common_keys)

    common_pairs: dict = {}
    if values_must_match:
        for key in common_keys_sorted:
            values = [env[key] for env in envs]
            if len(set(values)) == 1:
                common_pairs[key] = values[0]

    return {
        "common_keys": common_keys_sorted,
        "common_pairs": common_pairs,
        "vault_count": len(vault_names),
        "total_common": len(common_keys_sorted),
    }


def format_intersection_result(result: dict) -> str:
    lines = [
        f"Vaults compared : {result['vault_count']}",
        f"Common keys     : {result['total_common']}",
    ]
    if result["common_keys"]:
        lines.append("Keys: " + ", ".join(result["common_keys"]))
    if result["common_pairs"]:
        lines.append("Matching key=value pairs:")
        for k, v in result["common_pairs"].items():
            lines.append(f"  {k}={v}")
    return "\n".join(lines)
