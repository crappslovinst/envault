"""Tests for envault/cli_tokenize.py."""

import pytest
from unittest.mock import patch, MagicMock
from envault.cli_tokenize import cmd_tokenize
from envault.env_tokenize import TokenizeError

SAMPLE_TOKENIZED = {
    "APP_DB_HOST": {"tokens": ["APP", "DB", "HOST"], "depth": 3, "root": "APP", "leaf": "HOST"},
    "REDIS_URL": {"tokens": ["REDIS", "URL"], "depth": 2, "root": "REDIS", "leaf": "URL"},
}


@pytest.fixture
def mock_tokenize_fns():
    with patch("envault.cli_tokenize.tokenize_vault", return_value=SAMPLE_TOKENIZED) as tv, \
         patch("envault.cli_tokenize.get_token_roots", return_value=["APP", "REDIS"]) as gtr, \
         patch("envault.cli_tokenize.group_by_root", return_value={"APP": ["APP_DB_HOST"]}) as gbr, \
         patch("envault.cli_tokenize.format_tokenize_result", return_value="Tokenized keys:\n  ...") as fmt:
        yield {"tv": tv, "gtr": gtr, "gbr": gbr, "fmt": fmt}


def test_cmd_tokenize_ok(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass")
    assert result["ok"] is True
    assert result["vault"] == "myvault"
    assert result["total"] == 2


def test_cmd_tokenize_includes_formatted_by_default(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass")
    assert "formatted" in result


def test_cmd_tokenize_raw_skips_formatted(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass", raw=True)
    assert "formatted" not in result


def test_cmd_tokenize_includes_roots(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass")
    assert "APP" in result["roots"]
    assert "REDIS" in result["roots"]


def test_cmd_tokenize_group_flag(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass", group=True)
    assert "grouped" in result
    assert "APP" in result["grouped"]


def test_cmd_tokenize_no_group_by_default(mock_tokenize_fns):
    result = cmd_tokenize("myvault", "pass")
    assert "grouped" not in result


def test_cmd_tokenize_error_on_missing_vault():
    with patch("envault.cli_tokenize.tokenize_vault", side_effect=TokenizeError("not found")):
        result = cmd_tokenize("ghost", "pass")
        assert result["ok"] is False
        assert "not found" in result["error"]
