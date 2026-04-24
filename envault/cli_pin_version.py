"""CLI commands for vault version pinning."""

from envault.env_pin_version import (
    PinVersionError,
    set_version_pin,
    get_version_pin,
    clear_version_pin,
    check_version_compatible,
    format_version_info,
)


def cmd_set_version_pin(vault: str, password: str, version: str) -> dict:
    """Set a version pin on a vault."""
    try:
        result = set_version_pin(vault, password, version)
        result["ok"] = True
        return result
    except PinVersionError as e:
        return {"ok": False, "error": str(e)}


def cmd_get_version_pin(vault: str, password: str, formatted: bool = True) -> dict:
    """Get the version pin for a vault."""
    try:
        result = get_version_pin(vault, password)
        result["ok"] = True
        if formatted:
            result["formatted"] = format_version_info(result)
        return result
    except PinVersionError as e:
        return {"ok": False, "error": str(e)}


def cmd_clear_version_pin(vault: str, password: str) -> dict:
    """Clear the version pin from a vault."""
    try:
        result = clear_version_pin(vault, password)
        result["ok"] = True
        return result
    except PinVersionError as e:
        return {"ok": False, "error": str(e)}


def cmd_check_version(vault: str, password: str, required: str) -> dict:
    """Check if the vault's pinned version matches a required version."""
    try:
        result = check_version_compatible(vault, password, required)
        result["ok"] = True
        return result
    except PinVersionError as e:
        return {"ok": False, "error": str(e)}
