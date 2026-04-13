"""CLI operations for vault comparison."""

from envault.compare import compare_vaults, format_compare_result, CompareError


def cmd_compare(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: Optional[str] = None,
    show_unchanged: bool = False,
) -> dict:
    """Run a side-by-side comparison of two vaults.

    If password_b is omitted, password_a is reused (handy when both vaults
    share the same master password).
    """
    from typing import Optional  # local to avoid circular at module level

    resolved_pw_b = password_b if password_b is not None else password_a

    try:
        result = compare_vaults(vault_a, password_a, vault_b, resolved_pw_b)
    except CompareError as e:
        return {"error": str(e)}

    result["formatted"] = format_compare_result(result, show_unchanged=show_unchanged)
    return result
