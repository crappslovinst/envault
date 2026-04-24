from envault.env_diff_keys import diff_keys, format_diff_keys_result, DiffKeysError


def cmd_diff_keys(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: str,
    raw: bool = False,
) -> dict:
    """CLI handler: compare keys across two vaults."""
    try:
        result = diff_keys(vault_a, password_a, vault_b, password_b)
    except DiffKeysError as e:
        return {"ok": False, "error": str(e)}

    out = {"ok": True, **result}
    if not raw:
        out["formatted"] = format_diff_keys_result(result)
    return out
