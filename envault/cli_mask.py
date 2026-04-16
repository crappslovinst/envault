"""CLI commands for env masking."""

from envault.env_mask import mask_env, format_mask_result, MaskError


def cmd_mask(vault: str, password: str, show_partial: bool = False, keys: list = None, raw: bool = False) -> dict:
    """Mask sensitive values in a vault and return result."""
    try:
        masked = mask_env(vault, password, show_partial=show_partial, keys=keys)
    except MaskError as e:
        return {"ok": False, "error": str(e)}

    result = {"ok": True, "vault": vault, "masked": masked}
    if not raw:
        result["formatted"] = format_mask_result(masked)
    return result
