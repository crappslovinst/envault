"""cli_diff_keys.py — CLI wrapper for env_diff_keys."""

from envault.env_diff_keys import DiffKeysError, diff_keys, format_diff_keys_result


def cmd_diff_keys(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: str,
    raw: bool = False,
) -> dict:
    """Compare key sets of two vaults and return a result dict.

    Args:
        vault_a: Name of the first vault.
        password_a: Password for the first vault.
        vault_b: Name of the second vault.
        password_b: Password for the second vault.
        raw: If True, omit the human-readable 'formatted' field.

    Returns:
        Result dict with diff data and optionally a 'formatted' string.

    Raises:
        DiffKeysError: If either vault cannot be read.
    """
    try:
        result = diff_keys(vault_a, password_a, vault_b, password_b)
    except DiffKeysError:
        raise

    if not raw:
        result["formatted"] = format_diff_keys_result(result)

    return result
