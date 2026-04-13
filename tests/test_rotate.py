"""Tests for envault.rotate key rotation module."""

import pytest
from unittest.mock import patch, MagicMock

from envault.rotate import rotate_key, rotate_key_dry_run, VaultNotFoundError, RotationError


SAMPLE_DATA = {"DB_HOST": "localhost", "SECRET": "abc123", "PORT": "5432"}


@pytest.fixture
def mock_vault_ops():
    """Patch storage functions used by rotate."""
    with patch("envault.rotate.vault_exists") as mock_exists, \
         patch("envault.rotate.load_vault") as mock_load, \
         patch("envault.rotate.save_vault") as mock_save:
        mock_exists.return_value = True
        mock_load.return_value = SAMPLE_DATA.copy()
        yield mock_exists, mock_load, mock_save


def test_rotate_key_returns_summary(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    result = rotate_key("myapp", "old-pass", "new-pass")
    assert result["vault"] == "myapp"
    assert result["keys_rotated"] == len(SAMPLE_DATA)


def test_rotate_key_calls_save_with_new_password(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    rotate_key("myapp", "old-pass", "new-pass")
    mock_save.assert_called_once_with("myapp", SAMPLE_DATA, "new-pass")


def test_rotate_key_raises_if_vault_missing(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    mock_exists.return_value = False
    with pytest.raises(VaultNotFoundError, match="does not exist"):
        rotate_key("ghost", "old", "new")


def test_rotate_key_raises_on_bad_old_password(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    mock_load.side_effect = ValueError("bad decrypt")
    with pytest.raises(RotationError, match="Failed to decrypt"):
        rotate_key("myapp", "wrong-pass", "new-pass")


def test_rotate_key_raises_if_save_fails(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    mock_save.side_effect = IOError("disk full")
    with pytest.raises(RotationError, match="Failed to re-encrypt"):
        rotate_key("myapp", "old-pass", "new-pass")


def test_dry_run_returns_metadata(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    result = rotate_key_dry_run("myapp", "old-pass")
    assert result["vault"] == "myapp"
    assert result["keys_found"] == len(SAMPLE_DATA)
    assert result["dry_run"] is True


def test_dry_run_does_not_save(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    rotate_key_dry_run("myapp", "old-pass")
    mock_save.assert_not_called()


def test_dry_run_raises_if_vault_missing(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    mock_exists.return_value = False
    with pytest.raises(VaultNotFoundError):
        rotate_key_dry_run("ghost", "old-pass")


def test_dry_run_raises_on_bad_password(mock_vault_ops):
    mock_exists, mock_load, mock_save = mock_vault_ops
    mock_load.side_effect = ValueError("invalid token")
    with pytest.raises(RotationError, match="Old password is invalid"):
        rotate_key_dry_run("myapp", "wrong")
