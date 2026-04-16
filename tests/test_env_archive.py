import pytest
from unittest.mock import patch, MagicMock
from envault.env_archive import archive_vault, unarchive_vault, list_archived, ArchiveError, ARCHIVE_PREFIX


ENV_DATA = {"KEY": "value"}


@pytest.fixture
def mock_archive_deps():
    with patch("envault.env_archive.vault_exists") as exists, \
         patch("envault.env_archive.load_vault") as load, \
         patch("envault.env_archive.save_vault") as save, \
         patch("envault.env_archive.delete_vault") as delete, \
         patch("envault.env_archive.record_event") as audit:
        yield {"exists": exists, "load": load, "save": save, "delete": delete, "audit": audit}


def test_archive_returns_summary(mock_archive_deps):
    d = mock_archive_deps
    d["exists"].side_effect = lambda n: n == "myenv"
    d["load"].return_value = ENV_DATA
    result = archive_vault("myenv", "pass")
    assert result["status"] == "archived"
    assert result["vault"] == "myenv"
    assert ARCHIVE_PREFIX in result["archived_as"]


def test_archive_raises_if_vault_missing(mock_archive_deps):
    mock_archive_deps["exists"].return_value = False
    with pytest.raises(ArchiveError, match="not found"):
        archive_vault("ghost", "pass")


def test_archive_raises_if_already_archived(mock_archive_deps):
    d = mock_archive_deps
    d["exists"].return_value = True  # both original and archive exist
    with pytest.raises(ArchiveError, match="already archived"):
        archive_vault("myenv", "pass")


def test_archive_records_audit(mock_archive_deps):
    d = mock_archive_deps
    d["exists"].side_effect = lambda n: n == "myenv"
    d["load"].return_value = ENV_DATA
    archive_vault("myenv", "pass")
    d["audit"].assert_called_once()


def test_unarchive_returns_summary(mock_archive_deps):
    d = mock_archive_deps
    archived = f"{ARCHIVE_PREFIX}myenv"
    d["exists"].side_effect = lambda n: n == archived
    d["load"].return_value = ENV_DATA
    result = unarchive_vault("myenv", "pass")
    assert result["status"] == "unarchived"
    assert result["vault"] == "myenv"


def test_unarchive_raises_if_no_archive(mock_archive_deps):
    mock_archive_deps["exists"].return_value = False
    with pytest.raises(ArchiveError, match="No archive found"):
        unarchive_vault("ghost", "pass")


def test_unarchive_raises_if_target_exists(mock_archive_deps):
    d = mock_archive_deps
    d["exists"].return_value = True  # archive exists AND target exists
    with pytest.raises(ArchiveError, match="already exists"):
        unarchive_vault("myenv", "pass")


def test_list_archived_filters_correctly():
    vaults = ["prod", "__archived__staging", "dev", "__archived__qa"]
    result = list_archived(vaults)
    assert result == ["staging", "qa"]


def test_list_archived_empty():
    assert list_archived(["prod", "dev"]) == []
