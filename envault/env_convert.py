"""Convert vault env vars between naming conventions (snake_case, camelCase, SCREAMING_SNAKE)."""

import re
from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class ConvertError(Exception):
    pass


def _to_snake(key: str) -> str:
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', key)
    s = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
    return s.lower()


def _to_screaming_snake(key: str) -> str:
    return _to_snake(key).upper()


def _to_camel(key: str) -> str:
    parts = _to_snake(key).split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


_CONVERTERS = {
    'snake': _to_snake,
    'screaming_snake': _to_screaming_snake,
    'camel': _to_camel,
}


def convert_keys(vault: str, password: str, convention: str, dry_run: bool = False) -> dict:
    if convention not in _CONVERTERS:
        raise ConvertError(f"Unknown convention '{convention}'. Choose from: {list(_CONVERTERS)}.")
    if not vault_exists(vault):
        raise ConvertError(f"Vault '{vault}' not found.")

    env = get_env_vars(vault, password)
    fn = _CONVERTERS[convention]
    converted = {fn(k): v for k, v in env.items()}

    renamed = {k: fn(k) for k in env if fn(k) != k}
    collisions = len(env) - len(converted)

    if not dry_run and renamed:
        push_env(vault, password, converted)

    return {
        'vault': vault,
        'convention': convention,
        'renamed': renamed,
        'collisions': collisions,
        'total': len(converted),
        'dry_run': dry_run,
    }


def format_convert_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Convention : {result['convention']}",
        f"Keys renamed : {len(result['renamed'])}",
        f"Collisions : {result['collisions']}",
        f"Total keys : {result['total']}",
    ]
    if result['dry_run']:
        lines.append('(dry run — no changes written)')
    if result['renamed']:
        lines.append('Renamed:')
        for old, new in result['renamed'].items():
            lines.append(f'  {old} -> {new}')
    return '\n'.join(lines)
