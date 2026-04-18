import pytest
from unittest.mock import patch
from envault.env_dedupe import find_duplicate_values, dedupe_vault, format_dedupe_result, DedupeError

ENV = {
    "APP_HOST": "localhost",
    "DB_HOST": "localhost",
    "APP_PORT": "8080",
    "ALT_PORT": "8080",
    "SECRET": "abc123",
}


@pytest.fixture
def mock_deps():
    with patch("envault.env_dedupe.get_env_vars") as _get, \
         patch("envault.env_dedupe.push_env") as _push:
        _get.return_value = dict(ENV)
        yield _get, _push


def test_find_duplicates_detects_shared_values(mock_deps):
    _get, _ = mock_deps
    result = find_duplicate_values("myvault", "pass")
    assert "localhost" in result
    assert set(result["localhost"]) == {"APP_HOST", "DB_HOST"}
    assert "8080" in result
    assert set(result["8080"]) == {"APP_PORT", "ALT_PORT"}


def test_find_duplicates_excludes_unique_values(mock_deps):
    _get, _ = mock_deps
    result = find_duplicate_values("myvault", "pass")
    assert "abc123" not in result


def test_find_duplicates_raises_if_vault_missing():
    with patch("envault.env_dedupe.get_env_vars", return_value=None):
        with pytest.raises(DedupeError, match="not found"):
            find_duplicate_values("ghost", "pass")


def test_dedupe_keep_first_removes_later_keys(mock_deps):
    _get, _push = mock_deps
    result = dedupe_vault("myvault", "pass", keep="first")
    # sorted: ALT_PORT < APP_PORT, so ALT_PORT kept, APP_PORT removed
    assert "APP_PORT" in result["removed"]
    assert "ALT_PORT" in result["kept"]


def test_dedupe_keep_last_removes_earlier_keys(mock_deps):
    _get, _push = mock_deps
    result = dedupe_vault("myvault", "pass", keep="last")
    assert "ALT_PORT" in result["removed"]
    assert "APP_PORT" in result["kept"]


def test_dedupe_calls_push_when_changed(mock_deps):
    _get, _push = mock_deps
    dedupe_vault("myvault", "pass")
    _push.assert_called_once()


def test_dedupe_dry_run_skips_push(mock_deps):
    _get, _push = mock_deps
    result = dedupe_vault("myvault", "pass", dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_dedupe_raises_if_vault_missing():
    with patch("envault.env_dedupe.get_env_vars", return_value=None):
        with pytest.raises(DedupeError):
            dedupe_vault("ghost", "pass")


def test_format_dedupe_result_shows_removed(mock_deps):
    _get, _ = mock_deps
    result = dedupe_vault("myvault", "pass")
    text = format_dedupe_result(result)
    assert "Vault:" in text
    assert "Removed" in text


def test_format_dedupe_dry_run_label(mock_deps):
    _get, _ = mock_deps
    result = dedupe_vault("myvault", "pass", dry_run=True)
    text = format_dedupe_result(result)
    assert "dry run" in text
