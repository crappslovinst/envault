from envault.env_stats import StatsError, get_stats, format_stats


def cmd_stats(vault_name: str, password: str, raw: bool = False) -> dict:
    """CLI command: show statistical summary of a vault."""
    try:
        stats = get_stats(vault_name, password)
    except StatsError as e:
        return {"ok": False, "error": str(e)}

    result = {"ok": True, "stats": stats}
    if not raw:
        result["formatted"] = format_stats(stats)
    return result
