"""Promote env vars from one vault to another (e.g. staging -> production)."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists
from envault.audit import record_event


class PromoteError(Exception):
    pass


def promote_vault(
    src_vault: str,
    dst_vault: str,
    src_password: str,
    dst_password: str,
    keys: list[str] | None = None,
    overwrite: bool = True,
) -> dict:
    """Promote vars from src_vault to dst_vault.

    Args:
        src_vault: Name of the source vault.
        dst_vault: Name of the destination vault.
        src_password: Password for the source vault.
        dst_password: Password for the destination vault.
        keys: Optional list of specific keys to promote. If None, promote all.
        overwrite: If False, skip keys that already exist in dst.

    Returns:
        A summary dict with promoted, skipped, and missing keys.
    """
    if not vault_exists(src_vault):
        raise PromoteError(f"Source vault '{src_vault}' does not exist.")

    src_vars = get_env_vars(src_vault, src_password)

    dst_vars: dict[str, str] = {}
    if vault_exists(dst_vault):
        dst_vars = get_env_vars(dst_vault, dst_password)

    if keys is not None:
        missing = [k for k in keys if k not in src_vars]
        selected = {k: src_vars[k] for k in keys if k in src_vars}
    else:
        missing = []
        selected = dict(src_vars)

    promoted = []
    skipped = []

    merged = dict(dst_vars)
    for key, value in selected.items():
        if not overwrite and key in merged:
            skipped.append(key)
        else:
            merged[key] = value
            promoted.append(key)

    push_env(dst_vault, dst_password, merged)

    record_event(
        vault=dst_vault,
        action="promote",
        detail={
            "src_vault": src_vault,
            "promoted": promoted,
            "skipped": skipped,
            "missing": missing,
        },
    )

    return {
        "src_vault": src_vault,
        "dst_vault": dst_vault,
        "promoted": promoted,
        "skipped": skipped,
        "missing": missing,
    }
