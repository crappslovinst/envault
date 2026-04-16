import pytest
from unittest.mock import patch
from envault.cli_archive import cmd_archive, cmd_unarchive, cmd_list_archived, format_archive_list
from envault.env_archive import ArchiveError


@pytest.fixture
def mock_archive_fns():
    with patch("envault.cli_archive.archive_vault") as arch, \
         patch("envault.cli_archive.unarchive_vault") as unarch, \
         patch("envault.cli_archive.list_vaults") as lv, \
         patch("envault.cli_archive.list_archived") as la:
        yield {"archive": arch, "unarchive": unarch, "list_vaults": lv, "list_archived": la}


def test_cmd_archive_ok(mock_archive_fns):
    mock_archive_fns["archive"].return_value = {"status": "archived", "vault": "x", "archived_as": "__archived__x"}
    result = cmd_archive("x", "pass")
    assert result["status"] == "archived"


def test_cmd_archive_error(mock_archive_fns):
    mock_archive_fns["archive"].side_effect = ArchiveError("not found")
    result = cmd_archive("missing", "pass")
    assert result["status"] == "error"
    assert "not found" in result["message"]


def test_cmd_unarchive_ok(mock_archive_fns):
    mock_archive_fns["unarchive"].return_value = {"status": "unarchived", "vault": "x"}
    result = cmd_unarchive("x", "pass")
    assert result["status"] == "unarchived"


def test_cmd_unarchive_error(mock_archive_fns):
    mock_archive_fns["unarchive"].side_effect = ArchiveError("No archive found")
    result = cmd_unarchive("ghost", "pass")
    assert result["status"] == "error"


def test_cmd_list_archived_ok(mock_archive_fns):
    mock_archive_fns["list_vaults"].return_value = ["prod", "__archived__staging"]
    mock_archive_fns["list_archived"].return_value = ["staging"]
    result = cmd_list_archived()
    assert result["status"] == "ok"
    assert result["count"] == 1


def test_format_archive_list_empty():
    result = {"status": "ok", "archived": [], "count": 0}
    assert format_archive_list(result) == "No archived vaults."


def test_format_archive_list_with_items():
    result = {"status": "ok", "archived": ["staging", "qa"], "count": 2}
    output = format_archive_list(result)
    assert "staging" in output
    assert "qa" in output


def test_format_archive_list_error():
    result = {"status": "error", "message": "boom"}
    assert "Error" in format_archive_list(result)
