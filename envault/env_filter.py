"""Filter vault keys by prefix, suffix, or pattern."""

import re
from envault.vault_ops import get_env_vars


class FilterError(Exception):
    pass


def filter_env(
    vault: str,
    password: str,
    *,
    prefix: str = None,
    suffix: str = None,
    pattern: str = None,
    invert: bool = False,
) -> dict:
    """Return a filtered subset of env vars from a vault."""
    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise FilterError(str(e)) from e

    if not any([prefix, suffix, pattern]):
        raise FilterError("At least one of prefix, suffix, or pattern must be provided.")

    def matches(key: str) -> bool:
        if prefix and not key.startswith(prefix):
            return False
        if suffix and not key.endswith(suffix):
            return False
        if pattern:
            try:
                if not re.search(pattern, key):
                    return False
            except re.error as e:
                raise FilterError(f"Invalid regex pattern: {e}") from e
        return True

    result = {k: v for k, v in env.items() if matches(k) != invert}
    return result


def format_filter_result(filtered: dict, total: int) -> str:
    lines = [f"Matched {len(filtered)} of {total} keys:"]
    for k, v in sorted(filtered.items()):
        lines.append(f"  {k}={v}")
    return "\n".join(lines)
