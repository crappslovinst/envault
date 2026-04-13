"""CLI command for renaming a vault."""

from envault.rename import rename_vault, RenameError


def cmd_rename(src: str, dst: str, password: str) -> dict:
    """Rename a vault from `src` to `dst`.

    Args:
        src: Current vault name.
        dst: New vault name.
        password: Password for the vault.

    Returns:
        Result dict with 'success', 'message', and summary keys.
    """
    try:
        summary = rename_vault(src, dst, password)
        return {
            "success": True,
            "message": (
                f"Vault '{src}' renamed to '{dst}' "
                f"({summary['keys_moved']} key(s) moved)."
            ),
            **summary,
        }
    except RenameError as exc:
        return {
            "success": False,
            "message": str(exc),
        }
