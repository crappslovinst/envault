"""CLI commands for variable interpolation resolution."""

from envault.env_resolve import ResolveError, resolve_vars, find_references, format_resolve_result
from envault.vault_ops import get_env_vars


def cmd_resolve(vault_name: str, password: str, show_refs: bool = False) -> dict:
    """Resolve all ${VAR} references in a vault and return the result."""
    try:
        original = get_env_vars(vault_name, password)
        resolved = resolve_vars(vault_name, password)
    except ResolveError as e:
        return {"ok": False, "error": str(e)}

    result = {
        "ok": True,
        "vault": vault_name,
        "original": original,
        "resolved": resolved,
        "formatted": format_resolve_result(resolved, original),
    }

    if show_refs:
        result["references"] = find_references(original)

    return result


def cmd_find_refs(vault_name: str, password: str) -> dict:
    """List all keys that contain ${VAR} references."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    refs = find_references(env)
    return {
        "ok": True,
        "vault": vault_name,
        "references": refs,
        "count": len(refs),
    }
