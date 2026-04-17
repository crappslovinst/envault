from envault.env_default import DefaultError, set_defaults, get_defaults_preview, format_defaults_result


def cmd_set_defaults(
    vault: str,
    password: str,
    defaults: dict,
    overwrite: bool = False,
    dry_run: bool = False,
    raw: bool = False,
) -> dict:
    try:
        if dry_run:
            from envault.env_default import get_defaults_preview
            result = get_defaults_preview(vault, password, defaults)
            result["dry_run"] = True
            result["applied"] = result.pop("would_apply")
            result["skipped"] = result.pop("would_skip")
            result["total_applied"] = len(result["applied"])
            result["total_skipped"] = len(result["skipped"])
        else:
            result = set_defaults(vault, password, defaults, overwrite=overwrite)
            result["dry_run"] = False

        if not raw:
            result["formatted"] = format_defaults_result(result)
        return result
    except DefaultError as e:
        return {"ok": False, "error": str(e)}
