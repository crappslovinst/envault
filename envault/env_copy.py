"""Copy individual env vars between vaults."""

from envault.vault_ops import get_env_vars, push_env
from envault.audit import record_event


class CopyError(Exception):
    pass


def copy_keys(
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    keys: list[str],
    overwrite: bool = True,
) -> dict:
    """Copy specific keys from src_vault into dst_vault.

    Returns a summary dict with copied, skipped, and missing keys.
    """
    src_vars = get_env_vars(src_vault, src_password)
    if src_vars is None:
        raise CopyError(f"Source vault '{src_vault}' not found or wrong password.")

    try:
        dst_vars = get_env_vars(dst_vault, dst_password) or {}
    except Exception:
        dst_vars = {}

    copied = []
    skipped = []
    missing = []

    for key in keys:
        if key not in src_vars:
            missing.append(key)
            continue
        if key in dst_vars and not overwrite:
            skipped.append(key)
            continue
        dst_vars[key] = src_vars[key]
        copied.append(key)

    if copied:
        push_env(dst_vault, dst_password, dst_vars)
        record_event(
            dst_vault,
            "copy_keys",
            {"from": src_vault, "keys": copied},
        )

    return {
        "src_vault": src_vault,
        "dst_vault": dst_vault,
        "copied": copied,
        "skipped": skipped,
        "missing": missing,
    }


def copy_all(
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    overwrite: bool = True,
) -> dict:
    """Copy all env vars from src_vault into dst_vault."""
    src_vars = get_env_vars(src_vault, src_password)
    if src_vars is None:
        raise CopyError(f"Source vault '{src_vault}' not found or wrong password.")

    return copy_keys(
        src_vault,
        src_password,
        dst_vault,
        dst_password,
        keys=list(src_vars.keys()),
        overwrite=overwrite,
    )
