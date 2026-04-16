"""CLI operations for cascade vault resolution."""

from envault.env_cascade import CascadeError, resolve_cascade, resolve_cascade_with_sources


def cmd_cascade(
    vault_names: list[str],
    password: str,
    show_sources: bool = False,
) -> dict:
    """Resolve env vars from multiple vaults in priority order.

    Returns a result dict with merged vars and metadata.
    """
    try:
        if show_sources:
            detailed = resolve_cascade_with_sources(vault_names, password)
            return {
                "ok": True,
                "vaults": vault_names,
                "vars": {k: v["value"] for k, v in detailed.items()},
                "sources": {k: v["source"] for k, v in detailed.items()},
                "total": len(detailed),
            }
        else:
            merged = resolve_cascade(vault_names, password)
            return {
                "ok": True,
                "vaults": vault_names,
                "vars": merged,
                "total": len(merged),
            }
    except CascadeError as e:
        return {"ok": False, "error": str(e)}


def format_cascade_result(result: dict) -> str:
    """Format cascade result for display."""
    if not result.get("ok"):
        return f"[error] {result.get('error', 'unknown error')}"

    vaults_str = " -> ".join(result["vaults"])
    lines = [f"Cascade: {vaults_str}", f"Total keys: {result['total']}", ""]

    sources = result.get("sources", {})
    for key, value in sorted(result["vars"].items()):
        if sources:
            lines.append(f"  {key}={value}  (from: {sources[key]})")
        else:
            lines.append(f"  {key}={value}")

    return "\n".join(lines)
