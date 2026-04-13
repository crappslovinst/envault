"""Tests for envault/rename.py and envault/cli_rename.py."""

import pytest
from unittest.mock import patch, MagicMock

from envault.rename import rename_vault, RenameError
from envault.cli_rename import cmd_rename

SRC = "my-app"
DST = "my-app-renamed"
PASSWORD = "s3cr3t"
SAMPLE_DATA = {"DB_URL": "postgres://localhost/db", "SECRET": "abc123"}


@pytest.fixture()
def mock_rename_deps():
    with (
        patch("envault.rename.vault_exists") as mock_exists,
        patch("envault.rename.load_vault", return_value=SAMPLE_DATA) as mock_load,
        patch("envault.rename.save_vault") as mock_save,
        patch("envault.rename.record_event") as mock_audit,
        patch("envault.rename.os.remove") as mock_remove,
        patch("envault.rename._vault_path", side_effect=lambda n: f"/tmp/{n}.vault"),
    ):
        mock_exists.side_effect = lambda name: name == SRC
        yield {
            "exists": mock_exists,
            "load": mock_load,
            "save": mock_save,
            "audit": mock_audit,
            "remove": mock_remove,
        }


def test_rename_returns_summary(mock_rename_deps):
    result = rename_vault(SRC, DST, PASSWORD)
    assert result["src"] == SRC
    assert result["dst"] == DST
    assert result["keys_moved"] == len(SAMPLE_DATA)


def test_rename_saves_with_new_name(mock_rename_deps):
    rename_vault(SRC, DST, PASSWORD)
    mock_rename_deps["save"].assert_called_once_with(DST, SAMPLE_DATA, PASSWORD)


def test_rename_removes_old_vault(mock_rename_deps):
    rename_vault(SRC, DST, PASSWORD)
    mock_rename_deps["remove"].assert_called_once_with(f"/tmp/{SRC}.vault")


def test_rename_records_audit_event(mock_rename_deps):
    rename_vault(SRC, DST, PASSWORD)
    mock_rename_deps["audit"].assert_called_once_with(
        "rename", DST, {"src": SRC, "dst": DST}
    )


def test_rename_raises_if_src_missing(mock_rename_deps):
    mock_rename_deps["exists"].side_effect = lambda name: False
    with pytest.raises(RenameError, match="does not exist"):
        rename_vault(SRC, DST, PASSWORD)


def test_rename_raises_if_dst_exists(mock_rename_deps):
    mock_rename_deps["exists"].side_effect = lambda name: True  # both exist
    with pytest.raises(RenameError, match="already exists"):
        rename_vault(SRC, DST, PASSWORD)


def test_rename_raises_on_bad_password(mock_rename_deps):
    mock_rename_deps["load"].side_effect = Exception("Invalid token")
    with pytest.raises(RenameError, match="Could not load vault"):
        rename_vault(SRC, DST, PASSWORD)


def test_cmd_rename_success(mock_rename_deps):
    result = cmd_rename(SRC, DST, PASSWORD)
    assert result["success"] is True
    assert DST in result["message"]
    assert SRC in result["message"]


def test_cmd_rename_failure_returns_error(mock_rename_deps):
    mock_rename_deps["exists"].side_effect = lambda name: False
    result = cmd_rename(SRC, DST, PASSWORD)
    assert result["success"] is False
    assert "does not exist" in result["message"]
