"""Vault locking: prevent concurrent writes by using simple lock files."""

import os
import time
from pathlib import Path
from envault.storage import _vault_path

LOCK_TIMEOUT = 10  # seconds
LOCK_EXT = ".lock"


class LockError(Exception):
    pass


def _lock_path(vault_name: str) -> Path:
    return _vault_path(vault_name).with_suffix(LOCK_EXT)


def acquire_lock(vault_name: str, timeout: float = LOCK_TIMEOUT) -> Path:
    """Acquire a lock file for the given vault. Raises LockError on timeout."""
    lock = _lock_path(vault_name)
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            time.sleep(0.05)
    raise LockError(
        f"Could not acquire lock for vault '{vault_name}' within {timeout}s. "
        f"Lock file: {lock}"
    )


def release_lock(vault_name: str) -> None:
    """Release the lock file for the given vault. Silent if already gone."""
    lock = _lock_path(vault_name)
    try:
        lock.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_name: str) -> bool:
    """Return True if a lock file exists for the given vault."""
    return _lock_path(vault_name).exists()


class VaultLock:
    """Context manager for vault locking."""

    def __init__(self, vault_name: str, timeout: float = LOCK_TIMEOUT):
        self.vault_name = vault_name
        self.timeout = timeout
        self._lock_path: Path | None = None

    def __enter__(self) -> "VaultLock":
        self._lock_path = acquire_lock(self.vault_name, self.timeout)
        return self

    def __exit__(self, *_) -> None:
        release_lock(self.vault_name)
