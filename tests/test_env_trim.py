import pytest
from unittest.mock import patch, MagicMock
from envault.env_trim import trim_vault, find_duplicates, format_trim_result, TrimError


BASE_ENV = {
    "APP_NAME": "myapp",
    "DEBUG": "",
    "SECRET_KEY": "abc123",
    "app_name": "duplicate",
    "EMPTY_VAR": "  ",
}


@pytest.fixture
def mock_trim_deps():
    with patch("envault.env_trim.get_env_vars") as mock_get, \
         patch("envault.env_trim.push_env") as mock_push:
        yield mock_get, mock_push


def test_trim_removes_empty_values(mock_trim_deps):
    mock_get, mock_push = mock_trim_deps
    mock_get.return_value = {"A": "val", "B": "", "C": "  "}
    result = trim_vault("myvault", "pass", remove_empty=True, remove_duplicates=False)
    assert "B" in result["removed_empty"]
    assert "C" in result["removed_empty"]
    assert "A" not in result["removed_empty"]


def test_trim_removes_duplicate_keys(mock_trim_deps):
    mock_get, mock_push = mock_trim_deps
    mock_get.return_value = {"APP_NAME": "myapp", "app_name": "other"}
    result = trim_vault("myvault", "pass", remove_empty=False, remove_duplicates=True)
    assert len(result["removed_duplicates"]) == 1
    assert result["removed_duplicates"][0] == ("APP_NAME", "app_name")


def test_trim_dry_run_skips_push(mock_trim_deps):
    mock_get, mock_push = mock_trim_deps
    mock_get.return_value = {"X": "", "Y": "val"}
    result = trim_vault("myvault", "pass", dry_run=True)
    mock_push.assert_not_called()
    assert result["dry_run"] is True


def test_trim_calls_push_when_changed(mock_trim_deps):
    mock_get, mock_push = mock_trim_deps
    mock_get.return_value = {"A": "", "B": "keep"}
    trim_vault("myvault", "pass", remove_empty=True, dry_run=False)
    mock_push.assert_called_once()


def test_trim_no_changes_skips_push(mock_trim_deps):
    mock_get, mock_push = mock_trim_deps
    mock_get.return_value = {"A": "val", "B": "other"}
    result = trim_vault("myvault", "pass", remove_empty=True, remove_duplicates=True)
    mock_push.assert_not_called()
    assert result["changed"] is False


def test_trim_raises_on_bad_vault(mock_trim_deps):
    mock_get, _ = mock_trim_deps
    mock_get.side_effect = Exception("vault not found")
    with pytest.raises(TrimError, match="vault not found"):
        trim_vault("ghost", "pass")


def test_find_duplicates_detects_case_variants():
    env = {"KEY": "a", "key": "b", "OTHER": "c"}
    dupes = find_duplicates(env)
    assert len(dupes) == 1
    assert dupes[0] == ("KEY", "key")


def test_find_duplicates_no_dupes():
    env = {"A": "1", "B": "2", "C": "3"}
    assert find_duplicates(env) == []


def test_format_trim_result_nothing_to_trim():
    result = {
        "vault": "v", "removed_empty": [], "removed_duplicates": [],
        "total_removed": 0, "dry_run": False, "changed": False
    }
    out = format_trim_result(result)
    assert "Nothing to trim" in out


def test_format_trim_result_shows_dry_run():
    result = {
        "vault": "v", "removed_empty": ["X"], "removed_duplicates": [],
        "total_removed": 1, "dry_run": True, "changed": True
    }
    out = format_trim_result(result)
    assert "dry run" in out
    assert "X" in out
