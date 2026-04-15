"""Tests for envault/env_backup.py"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from envault.env_backup import backup_vault, restore_vault, BackupError


ENV_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


@pytest.fixture()
def mock_backup_deps(tmp_path):
    with (
        patch("envault.env_backup.vault_exists") as mock_exists,
        patch("envault.env_backup.get_env_vars") as mock_get,
        patch("envault.env_backup.push_env") as mock_push,
        patch("envault.env_backup.record_event") as mock_audit,
    ):
        mock_exists.return_value = True
        mock_get.return_value = ENV_VARS.copy()
        yield {
            "exists": mock_exists,
            "get": mock_get,
            "push": mock_push,
            "audit": mock_audit,
            "tmp": tmp_path,
        }


def test_backup_returns_summary(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    result = backup_vault("myapp", "pass", dest)
    assert result["vault"] == "myapp"
    assert result["keys_backed_up"] == 3
    assert result["dest"] == dest
    assert "backed_up_at" in result


def test_backup_writes_json_file(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    assert os.path.isfile(dest)
    with open(dest) as f:
        data = json.load(f)
    assert data["vault"] == "myapp"
    assert data["vars"] == ENV_VARS


def test_backup_raises_if_vault_missing(mock_backup_deps):
    mock_backup_deps["exists"].return_value = False
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    with pytest.raises(BackupError, match="does not exist"):
        backup_vault("ghost", "pass", dest)


def test_backup_records_audit_event(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    mock_backup_deps["audit"].assert_called_once_with("myapp", "backup", {"dest": dest})


def test_restore_returns_summary(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    mock_backup_deps["exists"].return_value = False
    result = restore_vault(dest, "myapp_restored", "newpass")
    assert result["vault"] == "myapp_restored"
    assert result["keys_restored"] == 3
    assert result["original_vault"] == "myapp"


def test_restore_calls_push(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    mock_backup_deps["exists"].return_value = False
    restore_vault(dest, "myapp_restored", "newpass")
    mock_backup_deps["push"].assert_called_once_with("myapp_restored", "newpass", ENV_VARS)


def test_restore_raises_if_file_missing(mock_backup_deps):
    with pytest.raises(BackupError, match="not found"):
        restore_vault("/nonexistent/path.json", "vault", "pass")


def test_restore_raises_on_existing_vault_without_overwrite(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    mock_backup_deps["exists"].return_value = True
    with pytest.raises(BackupError, match="already exists"):
        restore_vault(dest, "myapp", "pass", overwrite=False)


def test_restore_succeeds_with_overwrite(mock_backup_deps):
    dest = str(mock_backup_deps["tmp"] / "backup.json")
    backup_vault("myapp", "pass", dest)
    mock_backup_deps["exists"].return_value = True
    result = restore_vault(dest, "myapp", "pass", overwrite=True)
    assert result["keys_restored"] == 3


def test_restore_raises_on_invalid_json(mock_backup_deps, tmp_path):
    bad_file = str(tmp_path / "bad.json")
    with open(bad_file, "w") as f:
        f.write("not json at all")
    with pytest.raises(BackupError, match="Invalid backup file"):
        restore_vault(bad_file, "vault", "pass")
