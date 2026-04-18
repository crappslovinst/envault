"""CLI command for env_extract."""

from envault.env_extract import extract_keys, format_extract_result, ExtractError


def cmd_extract(src_vault: str, src_password: str, dst_vault: str, dst_password: str,
                keys: list[str], overwrite: bool = False, raw: bool = False) -> dict:
    """CLI entry point for extracting keys from one vault to another."""
    try:
        result = extract_keys(
            src_vault=src_vault,
            src_password=src_password,
            dst_vault=dst_vault,
            dst_password=dst_password,
            keys=keys,
            overwrite=overwrite,
        )
        if not raw:
            result["formatted"] = format_extract_result(result)
        return result
    except ExtractError as e:
        return {"ok": False, "error": str(e)}
