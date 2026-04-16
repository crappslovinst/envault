"""CLI commands for env filter feature."""

from envault.env_filter import FilterError, filter_env, format_filter_result
from envault.vault_ops import get_env_vars


def cmd_filter(
    vault: str,
    password: str,
    *,
    prefix: str = None,
    suffix: str = None,
    pattern: str = None,
    invert: bool = False,
    raw: bool = False,
) -> dict:
    """Filter vault keys and return result dict."""
    try:
        filtered = filter_env(
            vault,
            password,
            prefix=prefix,
            suffix=suffix,
            pattern=pattern,
            invert=invert,
        )
        total = len(get_env_vars(vault, password))
        result = {
            "ok": True,
            "vault": vault,
            "matched": len(filtered),
            "total": total,
            "keys": filtered,
        }
        if not raw:
            result["formatted"] = format_filter_result(filtered, total)
        return result
    except FilterError as e:
        return {"ok": False, "error": str(e)}
