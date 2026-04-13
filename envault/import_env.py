"""Import env vars into a vault from various sources."""

import json
from pathlib import Path
from typing import Optional

from envault.env_parser import parse_env
from envault.vault_ops import push_env


class ImportError(Exception):
    pass


def import_from_dotenv(vault_name: str, password: str, filepath: str) -> dict:
    """Import key-value pairs from a .env file into a vault."""
    path = Path(filepath)
    if not path.exists():
        raise ImportError(f"File not found: {filepath}")
    content = path.read_text(encoding="utf-8")
    data = parse_env(content)
    if not data:
        raise ImportError(f"No valid key-value pairs found in {filepath}")
    push_env(vault_name, password, data)
    return data


def import_from_json(vault_name: str, password: str, filepath: str) -> dict:
    """Import key-value pairs from a JSON file into a vault."""
    path = Path(filepath)
    if not path.exists():
        raise ImportError(f"File not found: {filepath}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ImportError(f"Invalid JSON: {e}") from e
    if not isinstance(raw, dict):
        raise ImportError("JSON root must be an object/dict")
    data = {str(k): str(v) for k, v in raw.items()}
    if not data:
        raise ImportError("JSON object is empty")
    push_env(vault_name, password, data)
    return data


def import_from_shell(vault_name: str, password: str, filepath: str) -> dict:
    """Import key-value pairs from a shell export file (export KEY=VALUE)."""
    path = Path(filepath)
    if not path.exists():
        raise ImportError(f"File not found: {filepath}")
    data: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            data[key] = value
    if not data:
        raise ImportError(f"No valid key-value pairs found in {filepath}")
    push_env(vault_name, password, data)
    return data
