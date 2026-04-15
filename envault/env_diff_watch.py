"""Live diff watching: monitor a .env file and report diffs against a vault on change."""

import time
import hashlib
from pathlib import Path
from typing import Callable, Optional

from envault.vault_ops import get_env_vars
from envault.diff import diff_envs, has_diff, format_diff
from envault.env_parser import parse_env
from envault.audit import record_event


class DiffWatchError(Exception):
    pass


def _file_hash(path: str) -> str:
    content = Path(path).read_bytes()
    return hashlib.sha256(content).hexdigest()


def watch_diff(
    vault_name: str,
    password: str,
    env_file: str,
    interval: float = 2.0,
    max_iterations: Optional[int] = None,
    on_diff: Optional[Callable[[dict], None]] = None,
) -> None:
    """Watch a .env file and emit diffs against a vault whenever it changes."""
    path = Path(env_file)
    if not path.exists():
        raise DiffWatchError(f"File not found: {env_file}")

    try:
        vault_env = get_env_vars(vault_name, password)
    except Exception as e:
        raise DiffWatchError(f"Could not load vault '{vault_name}': {e}")

    last_hash = _file_hash(env_file)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        iterations += 1

        current_hash = _file_hash(env_file)
        if current_hash == last_hash:
            continue

        last_hash = current_hash
        local_env = parse_env(path.read_text())
        result = diff_envs(vault_env, local_env)

        if has_diff(result):
            record_event(vault_name, "diff_watch_change", {"file": env_file})
            if on_diff:
                on_diff(result)


def snapshot_diff(vault_name: str, password: str, env_file: str) -> dict:
    """Return a one-shot diff between a vault and a local .env file."""
    path = Path(env_file)
    if not path.exists():
        raise DiffWatchError(f"File not found: {env_file}")

    try:
        vault_env = get_env_vars(vault_name, password)
    except Exception as e:
        raise DiffWatchError(f"Could not load vault '{vault_name}': {e}")

    local_env = parse_env(path.read_text())
    return diff_envs(vault_env, local_env)
