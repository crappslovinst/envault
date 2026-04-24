"""CLI command for numeric vault analysis."""

from envault.env_numeric import NumericError, analyze_numeric, format_numeric_result


def cmd_numeric(vault: str, password: str, prefix: str = "", raw: bool = False) -> dict:
    """
    Analyze numeric values in a vault.

    Returns a result dict; includes 'formatted' key unless raw=True.
    Raises NumericError on failure.
    """
    try:
        result = analyze_numeric(vault, password, prefix=prefix)
    except NumericError:
        raise

    if not raw:
        result["formatted"] = format_numeric_result(result)

    return result
