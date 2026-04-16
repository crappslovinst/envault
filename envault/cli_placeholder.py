"""CLI commands for placeholder detection and resolution."""

from envault.env_placeholder import (
    PlaceholderError,
    find_placeholders,
    format_placeholder_report,
    replace_placeholders,
)


def cmd_find_placeholders(vault_name: str, password: str, patterns: list[str] | None = None) -> dict:
    """Find unresolved placeholder values in a vault."""
    try:
        hits = find_placeholders(vault_name, password, patterns)
        return {
            "ok": True,
            "vault": vault_name,
            "placeholders": hits,
            "count": len(hits),
            "formatted": format_placeholder_report(hits),
        }
    except PlaceholderError as e:
        return {"ok": False, "error": str(e)}


def cmd_replace_placeholders(vault_name: str, password: str, replacements: dict[str, str]) -> dict:
    """Replace placeholder values in a vault with real values."""
    if not replacements:
        return {"ok": False, "error": "No replacements provided."}
    try:
        summary = replace_placeholders(vault_name, password, replacements)
        return {"ok": True, **summary}
    except PlaceholderError as e:
        return {"ok": False, "error": str(e)}
