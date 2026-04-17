import pytest
from unittest.mock import patch
from envault.cli_grep import cmd_grep


SAMPLE_RESULT = {
    "vault": "myvault",
    "pattern": "KEY",
    "total_keys": 4,
    "match_count": 2,
    "matches": [
        {"key": "SECRET_KEY", "value": "s", "matched_key": True, "matched_value": False},
        {"key": "API_KEY", "value": "k", "matched_key": True, "matched_value": False},
    ],
}


@pytest.fixture
def mock_grep():
    with patch("envault.cli_grep.grep_vault", return_value=SAMPLE_RESULT) as m:
        yield m


def test_cmd_grep_ok(mock_grep):
    result = cmd_grep("myvault", "pw", "KEY")
    assert result["ok"] is True
    assert result["match_count"] == 2


def test_cmd_grep_includes_formatted_by_default(mock_grep):
    result = cmd_grep("myvault", "pw", "KEY")
    assert "formatted" in result
    assert "myvault" in result["formatted"]


def test_cmd_grep_raw_skips_formatted(mock_grep):
    result = cmd_grep("myvault", "pw", "KEY", raw=True)
    assert "formatted" not in result


def test_cmd_grep_error_on_missing_vault():
    from envault.env_grep import GrepError
    with patch("envault.cli_grep.grep_vault", side_effect=GrepError("not found")):
        result = cmd_grep("missing", "pw", "x")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_cmd_grep_keys_only_passes_flags(mock_grep):
    cmd_grep("myvault", "pw", "KEY", keys_only=True)
    _, kwargs = mock_grep.call_args
    assert kwargs["search_keys"] is True
    assert kwargs["search_values"] is False


def test_cmd_grep_values_only_passes_flags(mock_grep):
    cmd_grep("myvault", "pw", "KEY", values_only=True)
    _, kwargs = mock_grep.call_args
    assert kwargs["search_keys"] is False
    assert kwargs["search_values"] is True
