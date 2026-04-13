"""Tests for envault/lock.py"""

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.lock import (
    acquire_lock,
    release_lock,
    is_locked,
    VaultLock,
    LockError,
    _lock_path,
)


@pytest.fixture(autouse=True)
def patch_vault_dir(tmp_path):
    """Redirect vault storage to a temp directory."""
    with patch("envault.lock._vault_path") as mock_vp:
        mock_vp.side_effect = lambda name: tmp_path / f"{name}.vault"
        yield tmp_path


def test_acquire_creates_lock_file(patch_vault_dir):
    lock = acquire_lock("myapp")
    assert lock.exists()
    release_lock("myapp")


def test_release_removes_lock_file(patch_vault_dir):
    acquire_lock("myapp")
    assert is_locked("myapp")
    release_lock("myapp")
    assert not is_locked("myapp")


def test_release_silent_if_no_lock(patch_vault_dir):
    # Should not raise even if lock doesn't exist
    release_lock("nonexistent")


def test_is_locked_false_initially(patch_vault_dir):
    assert not is_locked("myapp")


def test_is_locked_true_after_acquire(patch_vault_dir):
    acquire_lock("myapp")
    assert is_locked("myapp")
    release_lock("myapp")


def test_acquire_timeout_raises(patch_vault_dir):
    acquire_lock("myapp")  # hold the lock
    with pytest.raises(LockError, match="Could not acquire lock"):
        acquire_lock("myapp", timeout=0.1)
    release_lock("myapp")


def test_lock_file_contains_pid(patch_vault_dir):
    import os
    lock = acquire_lock("myapp")
    pid = int(lock.read_text())
    assert pid == os.getpid()
    release_lock("myapp")


def test_vault_lock_context_manager(patch_vault_dir):
    with VaultLock("myapp") as ctx:
        assert is_locked("myapp")
    assert not is_locked("myapp")


def test_vault_lock_releases_on_exception(patch_vault_dir):
    with pytest.raises(ValueError):
        with VaultLock("myapp"):
            assert is_locked("myapp")
            raise ValueError("boom")
    assert not is_locked("myapp")


def test_separate_vaults_have_separate_locks(patch_vault_dir):
    acquire_lock("app1")
    acquire_lock("app2")  # should not raise
    assert is_locked("app1")
    assert is_locked("app2")
    release_lock("app1")
    release_lock("app2")
