"""CLI commands for copying env vars between vaults."""

from envault.env_copy import copy_keys, copy_all, CopyError


def cmd_copy_keys(
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    keys: list[str],
    overwrite: bool = True,
) -> dict:
    """CLI entry point: copy specific keys between vaults."""
    try:
        result = copy_keys(
            src_vault, src_password, dst_vault, dst_password, keys, overwrite
        )
    except CopyError as e:
        return {"ok": False, "error": str(e)}

    lines = []
    if result["copied"]:
        lines.append(f"Copied {len(result['copied'])} key(s) to '{dst_vault}'.")
    if result["skipped"]:
        lines.append(f"Skipped {len(result['skipped'])} existing key(s) (overwrite=False).")
    if result["missing"]:
        lines.append(f"Missing in source: {', '.join(result['missing'])}.")

    return {
        "ok": True,
        "message": " ".join(lines) if lines else "Nothing to copy.",
        **result,
    }


def cmd_copy_all(
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    overwrite: bool = True,
) -> dict:
    """CLI entry point: copy all keys between vaults."""
    try:
        result = copy_all(src_vault, src_password, dst_vault, dst_password, overwrite)
    except CopyError as e:
        return {"ok": False, "error": str(e)}

    total = len(result["copied"]) + len(result["skipped"])
    return {
        "ok": True,
        "message": (
            f"Copied {len(result['copied'])}/{total} key(s) from '{src_vault}' "
            f"to '{dst_vault}'."
        ),
        **result,
    }
