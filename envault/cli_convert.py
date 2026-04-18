"""CLI wrapper for env key convention conversion."""

from envault.env_convert import convert_keys, format_convert_result, ConvertError


def cmd_convert(vault: str, password: str, convention: str, dry_run: bool = False, raw: bool = False) -> dict:
    """Convert all keys in a vault to a naming convention.

    convention: 'snake' | 'screaming_snake' | 'camel'
    """
    try:
        result = convert_keys(vault, password, convention, dry_run=dry_run)
    except ConvertError as e:
        return {'ok': False, 'error': str(e)}

    out = {'ok': True, **result}
    if not raw:
        out['formatted'] = format_convert_result(result)
    return out
