"""CLI commands for managing vault read-only mode."""

from envault.env_readonly import (
    ReadonlyError,
    set_readonly,
    get_readonly,
    format_readonly_info,
)


def cmd_set_readonly(vault: str, password: str, enable: bool = True) -> dict:
    """Enable or disable read-only mode for a vault."""
    try:
        result = set_readonly(vault, password, readonly=enable)
        return {"ok": True, **result}
    except ReadonlyError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_get_readonly(vault: str, password: str, raw: bool = False) -> dict:
    """Return the read-only status of a vault."""
    try:
        info = get_readonly(vault, password)
        result = {"ok": True, **info}
        if not raw:
            result["formatted"] = format_readonly_info(info)
        return result
    except ReadonlyError as exc:
        return {"ok": False, "error": str(exc)}
