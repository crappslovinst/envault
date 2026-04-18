"""Extract a subset of keys from a vault into a new vault."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class ExtractError(Exception):
    pass


def extract_keys(src_vault: str, src_password: str, dst_vault: str, dst_password: str,
                 keys: list[str], overwrite: bool = False) -> dict:
    """Extract specific keys from src_vault into dst_vault."""
    if not vault_exists(src_vault):
        raise ExtractError(f"Source vault '{src_vault}' not found.")

    src_env = get_env_vars(src_vault, src_password)

    found = {}
    missing = []
    for key in keys:
        if key in src_env:
            found[key] = src_env[key]
        else:
            missing.append(key)

    if not found:
        raise ExtractError("None of the requested keys exist in the source vault.")

    if vault_exists(dst_vault) and not overwrite:
        existing = get_env_vars(dst_vault, dst_password)
        merged = {**found, **existing}
    else:
        merged = found

    push_env(dst_vault, dst_password, merged)

    return {
        "src_vault": src_vault,
        "dst_vault": dst_vault,
        "extracted": list(found.keys()),
        "missing": missing,
        "total_extracted": len(found),
    }


def format_extract_result(result: dict) -> str:
    lines = [
        f"Extracted {result['total_extracted']} key(s) from '{result['src_vault']}' → '{result['dst_vault']}'",
        f"  Keys: {', '.join(result['extracted'])}",
    ]
    if result["missing"]:
        lines.append(f"  Missing: {', '.join(result['missing'])}")
    return "\n".join(lines)
