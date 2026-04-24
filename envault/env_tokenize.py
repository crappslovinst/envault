"""Tokenize vault keys into structured name segments."""

from typing import Optional
from envault.vault_ops import get_env_vars


class TokenizeError(Exception):
    pass


def _split_token(key: str, delimiter: str = "_") -> list[str]:
    """Split a key into tokens by delimiter."""
    return [p for p in key.split(delimiter) if p]


def tokenize_vault(
    vault_name: str,
    password: str,
    delimiter: str = "_",
    prefix_filter: Optional[str] = None,
) -> dict:
    """Return token breakdown for all keys in a vault."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise TokenizeError(str(e)) from e

    if not env:
        raise TokenizeError(f"Vault '{vault_name}' is empty.")

    results = {}
    for key in env:
        if prefix_filter and not key.startswith(prefix_filter):
            continue
        tokens = _split_token(key, delimiter)
        results[key] = {
            "tokens": tokens,
            "depth": len(tokens),
            "root": tokens[0] if tokens else "",
            "leaf": tokens[-1] if tokens else "",
        }

    return results


def get_token_roots(tokenized: dict) -> list[str]:
    """Return unique root tokens across all keys."""
    return sorted({v["root"] for v in tokenized.values() if v["root"]})


def group_by_root(tokenized: dict) -> dict:
    """Group keys by their root token."""
    groups: dict[str, list[str]] = {}
    for key, info in tokenized.items():
        root = info["root"]
        groups.setdefault(root, []).append(key)
    return {r: sorted(keys) for r, keys in sorted(groups.items())}


def format_tokenize_result(tokenized: dict) -> str:
    """Format tokenized keys for display."""
    if not tokenized:
        return "No keys to tokenize."
    lines = []
    for key, info in sorted(tokenized.items()):
        tokens_str = " > ".join(info["tokens"])
        lines.append(f"  {key}: [{tokens_str}] (depth={info['depth']})")
    return "Tokenized keys:\n" + "\n".join(lines)
