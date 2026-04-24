"""Numeric analysis for vault values — sum, average, min, max over castable keys."""

from envault.vault_ops import get_env_vars


class NumericError(Exception):
    pass


def analyze_numeric(vault_name: str, password: str, prefix: str = "") -> dict:
    """Return numeric stats for all keys whose values are valid numbers."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as exc:
        raise NumericError(str(exc)) from exc

    numeric = {}
    for k, v in env.items():
        if prefix and not k.startswith(prefix):
            continue
        try:
            numeric[k] = float(v)
        except (ValueError, TypeError):
            pass

    if not numeric:
        return {
            "vault": vault_name,
            "prefix": prefix or None,
            "numeric_keys": [],
            "count": 0,
            "sum": None,
            "min": None,
            "max": None,
            "average": None,
        }

    values = list(numeric.values())
    return {
        "vault": vault_name,
        "prefix": prefix or None,
        "numeric_keys": sorted(numeric.keys()),
        "count": len(values),
        "sum": sum(values),
        "min": min(values),
        "max": max(values),
        "average": sum(values) / len(values),
    }


def format_numeric_result(result: dict) -> str:
    if result["count"] == 0:
        return f"[{result['vault']}] No numeric values found."
    lines = [
        f"[{result['vault']}] Numeric analysis ({result['count']} keys):",
        f"  keys   : {', '.join(result['numeric_keys'])}",
        f"  sum    : {result['sum']}",
        f"  min    : {result['min']}",
        f"  max    : {result['max']}",
        f"  average: {result['average']:.4f}",
    ]
    return "\n".join(lines)
