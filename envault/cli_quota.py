from envault.env_quota import check_quota, format_quota_result, QuotaError


def cmd_quota(
    vault_name: str,
    password: str,
    max_keys: int = 100,
    max_value_length: int = 1024,
    raw: bool = False,
) -> dict:
    try:
        result = check_quota(
            vault_name,
            password,
            max_keys=max_keys,
            max_value_length=max_value_length,
        )
    except QuotaError as e:
        return {"ok": False, "error": str(e)}

    if not raw:
        result["formatted"] = format_quota_result(result)
    return result
