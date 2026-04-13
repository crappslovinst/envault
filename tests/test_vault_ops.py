"""Tests for envault.vault_ops (push/pull/get)."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envault import vault_ops
from envault.vault_ops import push_env, pull_env, get_env_vars


PASSWORD = "test-password-123"
VAULT_NAME = "test_vault"
SAMPLE_ENV = "API_KEY=abc123\nDEBUG=true\nPORT=8080\n"


@pytest.fixture(autouse=True)
def patch_vault_dir(tmp_path):
    """Redirect all vault storage to a temp directory."""
    with patch("envault.storage.VAULT_DIR", tmp_path):
        yield tmp_path


def test_push_returns_parsed_data():
    result = push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    assert result == {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}


def test_push_from_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    result = push_env(VAULT_NAME, PASSWORD, env_path=env_file)
    assert result["API_KEY"] == "abc123"


def test_pull_writes_env_file(tmp_path):
    push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    out_file = tmp_path / ".env"
    result = pull_env(VAULT_NAME, PASSWORD, env_path=out_file)
    assert out_file.exists()
    assert result["API_KEY"] == "abc123"


def test_pull_raises_if_vault_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        pull_env("nonexistent", PASSWORD, env_path=tmp_path / ".env")


def test_pull_raises_if_file_exists_no_overwrite(tmp_path):
    push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    out_file = tmp_path / ".env"
    out_file.write_text("existing content")
    with pytest.raises(FileExistsError):
        pull_env(VAULT_NAME, PASSWORD, env_path=out_file, overwrite=False)


def test_pull_overwrites_when_flag_set(tmp_path):
    push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    out_file = tmp_path / ".env"
    out_file.write_text("old=data")
    pull_env(VAULT_NAME, PASSWORD, env_path=out_file, overwrite=True)
    content = out_file.read_text()
    assert "API_KEY" in content


def test_get_env_vars_returns_dict():
    push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    result = get_env_vars(VAULT_NAME, PASSWORD)
    assert result == {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}


def test_get_env_vars_wrong_password_raises():
    push_env(VAULT_NAME, PASSWORD, env_content=SAMPLE_ENV)
    with pytest.raises(Exception):
        get_env_vars(VAULT_NAME, "wrong-password")
