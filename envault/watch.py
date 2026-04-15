"""Watch a .env file for changes and auto-push to a vault."""

import os
import time
import hashlib
from typing import Optional, Callable

from envault.vault_ops import push_env
from envault.audit import record_event


class WatchError(Exception):
    pass


def _file_hash(path: str) -> str:
    """Return MD5 hash of file contents."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def watch_env(
    env_path: str,
    vault_name: str,
    password: str,
    interval: float = 2.0,
    max_events: Optional[int] = None,
    on_change: Optional[Callable[[str, dict], None]] = None,
) -> list[dict]:
    """
    Poll `env_path` every `interval` seconds and push to `vault_name` on change.

    Returns a list of push-event dicts recorded during the watch session.
    Stops after `max_events` pushes if provided (useful for testing).
    Calls `on_change(env_path, push_result)` after each push if provided.
    Raises WatchError if the file does not exist at start.
    """
    if not os.path.isfile(env_path):
        raise WatchError(f"File not found: {env_path}")

    last_hash = _file_hash(env_path)
    events: list[dict] = []

    while True:
        time.sleep(interval)

        if not os.path.isfile(env_path):
            raise WatchError(f"Watched file disappeared: {env_path}")

        current_hash = _file_hash(env_path)
        if current_hash == last_hash:
            continue

        last_hash = current_hash
        result = push_env(vault_name, password, env_path=env_path)
        event = record_event(
            vault=vault_name,
            action="watch_push",
            detail={"file": env_path, "keys": list(result.keys())},
        )
        events.append(event)

        if on_change:
            on_change(env_path, result)

        if max_events is not None and len(events) >= max_events:
            break

    return events
