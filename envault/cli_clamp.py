"""CLI wrapper for the clamp feature."""

from envault.env_clamp import ClampError, clamp_values, format_clamp_result


def cmd_clamp(
    vault: str,
    password: str,
    min_len: int = 0,
    max_len: int = 255,
    pad_char: str = " ",
    dry_run: bool = False,
    raw: bool = False,
) -> dict:
    """Clamp vault values to [min_len, max_len].

    Returns the raw summary dict; adds a 'formatted' key unless *raw* is True.
    Raises ClampError on failure.
    """
    try:
        result = clamp_values(
            vault,
            password,
            min_len=min_len,
            max_len=max_len,
            pad_char=pad_char,
            dry_run=dry_run,
        )
    except ClampError:
        raise

    if not raw:
        result["formatted"] = format_clamp_result(result)
    return result
