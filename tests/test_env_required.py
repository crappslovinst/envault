"""Tests for envault.env_required."""

import pytest
from unittest.mock import patch

from envault.env_required import (
    RequiredError,
    check_required,
    enforce_required,
    format_required_result,
)

VAULT = "myvault"
PASS = "secret"
ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "abc123"}


@pytest.fixture
def mock_deps():
    with patch("envault.env_required.vault_exists", return_value=True) as _exists, \
         patch("envault.env_required.get_env_vars", return_value=ENV) as _get:
        yield _exists, _get


def test_check_required_all_present(mock_deps):
    result = check_required(VAULT, PASS, ["DB_HOST", "API_KEY"])
    assert result["ok"] is True
    assert result["missing"] == []
    assert set(result["present"]) == {"DB_HOST", "API_KEY"}


def test_check_required_some_missing(mock_deps):
    result = check_required(VAULT, PASS, ["DB_HOST", "SECRET_KEY"])
    assert result["ok"] is False
    assert "SECRET_KEY" in result["missing"]
    assert "DB_HOST" in result["present"]


def test_check_required_all_missing(mock_deps):
    result = check_required(VAULT, PASS, ["MISSING_A", "MISSING_B"])
    assert result["ok"] is False
    assert len(result["missing"]) == 2
    assert result["present"] == []


def test_check_required_raises_if_vault_missing():
    with patch("envault.env_required.vault_exists", return_value=False):
        with pytest.raises(RequiredError, match="not found"):
            check_required(VAULT, PASS, ["DB_HOST"])


def test_enforce_required_passes_when_all_present(mock_deps):
    result = enforce_required(VAULT, PASS, ["DB_HOST", "API_KEY"])
    assert result["ok"] is True


def test_enforce_required_raises_when_missing(mock_deps):
    with pytest.raises(RequiredError, match="missing required keys"):
        enforce_required(VAULT, PASS, ["DB_HOST", "MISSING_KEY"])


def test_format_required_result_ok(mock_deps):
    result = check_required(VAULT, PASS, ["DB_HOST"])
    formatted = format_required_result(result)
    assert "Status: OK" in formatted
    assert "DB_HOST" not in formatted or "Missing" not in formatted


def test_format_required_result_fail(mock_deps):
    result = check_required(VAULT, PASS, ["DB_HOST", "GHOST_KEY"])
    formatted = format_required_result(result)
    assert "Status: FAIL" in formatted
    assert "GHOST_KEY" in formatted


def test_check_required_returns_vault_name(mock_deps):
    result = check_required(VAULT, PASS, ["DB_HOST"])
    assert result["vault"] == VAULT


def test_check_required_empty_list(mock_deps):
    result = check_required(VAULT, PASS, [])
    assert result["ok"] is True
    assert result["missing"] == []
    assert result["present"] == []
