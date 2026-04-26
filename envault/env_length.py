"""Analyze and enforce value length constraints in a vault."""

from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class LengthError(Exception):
    pass


def analyze_lengths(vault_name: str, password: str) -> dict:
    """Return length stats for all values in the vault."""
    if not vault_exists(vault_name):
        raise LengthError(f"Vault '{vault_name}' not found")

    env = get_env_vars(vault_name, password)
    if not env:
        return {"total": 0, "min": None, "max": None, "avg": None, "entries": []}

    entries = [
        {"key": k, "value": v, "length": len(v)}
        for k, v in env.items()
    ]
    lengths = [e["length"] for e in entries]

    return {
        "total": len(entries),
        "min": min(lengths),
        "max": max(lengths),
        "avg": round(sum(lengths) / len(lengths), 2),
        "entries": sorted(entries, key=lambda e: e["length"], reverse=True),
    }


def check_length_limits(
    vault_name: str,
    password: str,
    min_length: int = 0,
    max_length: int = 0,
) -> dict:
    """Check which keys violate min/max length constraints."""
    if min_length < 0 or max_length < 0:
        raise LengthError("min_length and max_length must be non-negative")
    if max_length and min_length > max_length:
        raise LengthError("min_length cannot exceed max_length")

    if not vault_exists(vault_name):
        raise LengthError(f"Vault '{vault_name}' not found")

    env = get_env_vars(vault_name, password)
    violations = []

    for k, v in env.items():
        length = len(v)
        if min_length and length < min_length:
            violations.append({"key": k, "length": length, "reason": f"below min ({min_length})"})
        elif max_length and length > max_length:
            violations.append({"key": k, "length": length, "reason": f"above max ({max_length})"})

    return {
        "vault": vault_name,
        "checked": len(env),
        "violations": violations,
        "ok": len(violations) == 0,
    }


def format_length_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}  checked={result['checked']}"]
    if result["ok"]:
        lines.append("  All values within length limits.")
    else:
        for v in result["violations"]:
            lines.append(f"  {v['key']}: length={v['length']}  ({v['reason']})")
    return "\n".join(lines)
