"""Tests for envault.clone and envault.cli_clone."""

import pytest
from unittest.mock import patch, MagicMock

from envault.clone import clone_vault, CloneError
from envault.cli_clone import cmd_clone


ENV_VARS = {"APP_ENV": "production", "SECRET": "abc123", "PORT": "8080"}


@pytest.fixture()
 def mock_clone_deps():
    with (
        patch("envault.clone.vault_exists") as mock_exists,
        patch("envault.clone.get_env_vars", return_value=ENV_VARS) as mock_get,
        patch("envault.clone.push_env") as mock_push,
        patch("envault.clone.record_event") as mock_record,
    ):
        # src exists, dst does not
        mock_exists.side_effect = lambda name: name == "my-vault"
        yield {
            "exists": mock_exists,
            "get_env_vars": mock_get,
            "push_env": mock_push,
            "record_event": mock_record,
        }


def test_clone_returns_summary(mock_clone_deps):
    result = clone_vault("my-vault", "my-vault-copy", "pass123")
    assert result["source"] == "my-vault"
    assert result["destination"] == "my-vault-copy"
    assert result["keys_copied"] == len(ENV_VARS)


def test_clone_calls_push_with_env_vars(mock_clone_deps):
    clone_vault("my-vault", "my-vault-copy", "pass123")
    mock_clone_deps["push_env"].assert_called_once_with(
        "my-vault-copy", "pass123", ENV_VARS
    )


def test_clone_uses_custom_dst_password(mock_clone_deps):
    clone_vault("my-vault", "my-vault-copy", "old-pass", dst_password="new-pass")
    mock_clone_deps["push_env"].assert_called_once_with(
        "my-vault-copy", "new-pass", ENV_VARS
    )


def test_clone_records_audit_event(mock_clone_deps):
    clone_vault("my-vault", "my-vault-copy", "pass123")
    mock_clone_deps["record_event"].assert_called_once()
    call_kwargs = mock_clone_deps["record_event"].call_args.kwargs
    assert call_kwargs["vault"] == "my-vault-copy"
    assert call_kwargs["action"] == "clone"


def test_clone_raises_if_src_missing(mock_clone_deps):
    with pytest.raises(CloneError, match="does not exist"):
        clone_vault("nonexistent", "copy", "pass")


def test_clone_raises_if_dst_exists(mock_clone_deps):
    # Make dst also appear to exist
    mock_clone_deps["exists"].side_effect = lambda name: True
    with pytest.raises(CloneError, match="already exists"):
        clone_vault("my-vault", "my-vault", "pass")


def test_cmd_clone_returns_string(mock_clone_deps):
    msg = cmd_clone("my-vault", "my-vault-copy", "pass123")
    assert "my-vault" in msg
    assert "my-vault-copy" in msg
    assert "3 key(s)" in msg


def test_cmd_clone_notes_same_password(mock_clone_deps):
    msg = cmd_clone("my-vault", "my-vault-copy", "pass123")
    assert "same password" in msg


def test_cmd_clone_notes_new_password(mock_clone_deps):
    msg = cmd_clone("my-vault", "my-vault-copy", "old", dst_password="new")
    assert "new password" in msg
