"""CLI commands for vault key sorting."""

from envault.env_sort import SortError, sort_vault, format_sort_result


def cmd_sort(
    vault: str,
    password: str,
    reverse: bool = False,
    group_by_prefix: bool = False,
    dry_run: bool = False,
    raw: bool = False,
) -> dict:
    try:
        result = sort_vault(
            vault,
            password,
            reverse=reverse,
            group_by_prefix=group_by_prefix,
            dry_run=dry_run,
        )
        if not raw:
            result["formatted"] = format_sort_result(result)
        return {"ok": True, "result": result}
    except SortError as e:
        return {"ok": False, "error": str(e)}
