"""Tests for envault.env_fmt."""

import pytest
from unittest.mock import patch

from envault.env_fmt import FmtError, format_vault


@pytest.fixture
def mock_fmt_deps():
    with patch("envault.env_fmt.get_env_vars") as mock_get, \
         patch("envault.env_fmt.push_env") as mock_push:
        yield mock_get, mock_push


def test_format_vault_uppercases_keys(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"db_host": "localhost", "db_port": "5432"}
    result = format_vault("myapp", "secret")
    assert "DB_HOST" in result["formatted"]
    assert "DB_PORT" in result["formatted"]


def test_format_vault_strips_value_whitespace(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"API_KEY": "  abc123  "}
    result = format_vault("myapp", "secret")
    assert result["formatted"]["API_KEY"] == "abc123"


def test_format_vault_calls_push_when_changes(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"key": "value"}
    format_vault("myapp", "secret")
    mock_push.assert_called_once()


def test_format_vault_dry_run_skips_push(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"key": "value"}
    result = format_vault("myapp", "secret", dry_run=True)
    mock_push.assert_not_called()
    assert result["dry_run"] is True


def test_format_vault_no_changes_skips_push(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"KEY": "value"}
    format_vault("myapp", "secret")
    mock_push.assert_not_called()


def test_format_vault_raises_on_bad_vault(mock_fmt_deps):
    mock_get, _ = mock_fmt_deps
    mock_get.side_effect = Exception("vault not found")
    with pytest.raises(FmtError, match="vault not found"):
        format_vault("missing", "secret")


def test_format_vault_returns_total_keys(mock_fmt_deps):
    mock_get, mock_push = mock_fmt_deps
    mock_get.return_value = {"A": "1", "B": "2", "C": "3"}
    result = format_vault("myapp", "secret")
    assert result["total_keys"] == 3
