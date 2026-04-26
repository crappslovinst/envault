"""CLI commands for value-length analysis and enforcement."""

from envault.env_length import analyze_lengths, check_length_limits, format_length_result, LengthError


def cmd_analyze_lengths(vault: str, password: str, raw: bool = False) -> dict:
    """Return length statistics for every value in the vault."""
    try:
        result = analyze_lengths(vault, password)
        if not raw:
            lines = [f"Total keys : {result['total']}"]
            if result["total"]:
                lines.append(f"Min length : {result['min']}")
                lines.append(f"Max length : {result['max']}")
                lines.append(f"Avg length : {result['avg']}")
                lines.append("Top 5 longest values:")
                for e in result["entries"][:5]:
                    lines.append(f"  {e['key']}: {e['length']} chars")
            result["formatted"] = "\n".join(lines)
        return result
    except LengthError as exc:
        raise exc


def cmd_check_lengths(
    vault: str,
    password: str,
    min_length: int = 0,
    max_length: int = 0,
    raw: bool = False,
) -> dict:
    """Check vault values against min/max length constraints."""
    try:
        result = check_length_limits(vault, password, min_length=min_length, max_length=max_length)
        if not raw:
            result["formatted"] = format_length_result(result)
        return result
    except LengthError as exc:
        raise exc
