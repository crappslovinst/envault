"""Tests for envault.env_normalize."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_normalize import (
    NormalizeError,
    normalize_vault,
    format_normalize_result,
    _normalize_value,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_deps(exists=True, env=None):
    env = env or {}
    with patch("envault.env_normalize.vault_exists", return_value=exists) as mock_exists, \
         patch("envault.env_normalize.get_env_vars", return_value=env) as mock_get, \
         patch("envault.env_normalize.push_env") as mock_push:
        yield mock_exists, mock_get, mock_push


# ---------------------------------------------------------------------------
# _normalize_value unit tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("  hello  ", "hello"),
    ("True", "true"),
    ("YES", "true"),
    ("1", "true"),
    ("ON", "true"),
    ("False", "false"),
    ("NO", "false"),
    ("0", "false"),
    ("OFF", "false"),
    ("  somevalue  ", "somevalue"),
])
def test_normalize_value_bools_and_whitespace(raw, expected):
    assert _normalize_value(raw, normalize_bools=True) == expected


def test_normalize_value_skip_bools():
    assert _normalize_value("True", normalize_bools=False) == "True"
    assert _normalize_value("  yes  ", normalize_bools=False) == "yes"


# ---------------------------------------------------------------------------
# normalize_vault tests
# ---------------------------------------------------------------------------

def test_normalize_raises_if_vault_missing():
    with patch("envault.env_normalize.vault_exists", return_value=False):
        with pytest.raises(NormalizeError, match="not found"):
            normalize_vault("ghost", "pw")


def test_normalize_returns_summary():
    env = {"DEBUG": "True", "NAME": "  app  "}
    with patch("envault.env_normalize.vault_exists", return_value=True), \
         patch("envault.env_normalize.get_env_vars", return_value=env), \
         patch("envault.env_normalize.push_env") as mock_push:
        result = normalize_vault("myapp", "pw")

    assert result["vault"] == "myapp"
    assert result["total"] == 2
    assert result["changed"] == 2
    assert set(result["changed_keys"]) == {"DEBUG", "NAME"}
    assert result["dry_run"] is False
    mock_push.assert_called_once()


def test_normalize_dry_run_skips_push():
    env = {"ACTIVE": "yes"}
    with patch("envault.env_normalize.vault_exists", return_value=True), \
         patch("envault.env_normalize.get_env_vars", return_value=env), \
         patch("envault.env_normalize.push_env") as mock_push:
        result = normalize_vault("myapp", "pw", dry_run=True)

    mock_push.assert_not_called()
    assert result["dry_run"] is True
    assert result["changed"] == 1


def test_normalize_no_changes_skips_push():
    env = {"KEY": "value"}
    with patch("envault.env_normalize.vault_exists", return_value=True), \
         patch("envault.env_normalize.get_env_vars", return_value=env), \
         patch("envault.env_normalize.push_env") as mock_push:
        result = normalize_vault("myapp", "pw")

    mock_push.assert_not_called()
    assert result["changed"] == 0
    assert result["changed_keys"] == []


def test_normalize_skips_bool_normalization_when_disabled():
    env = {"FLAG": "yes"}
    with patch("envault.env_normalize.vault_exists", return_value=True), \
         patch("envault.env_normalize.get_env_vars", return_value=env), \
         patch("envault.env_normalize.push_env") as mock_push:
        result = normalize_vault("myapp", "pw", normalize_bools=False)

    mock_push.assert_not_called()
    assert result["changed"] == 0


# ---------------------------------------------------------------------------
# format_normalize_result tests
# ---------------------------------------------------------------------------

def test_format_normalize_result_includes_vault_and_counts():
    result = {
        "vault": "prod",
        "total": 10,
        "changed": 3,
        "changed_keys": ["A", "B", "C"],
        "dry_run": False,
    }
    output = format_normalize_result(result)
    assert "prod" in output
    assert "10" in output
    assert "3" in output
    assert "A, B, C" in output


def test_format_normalize_result_dry_run_note():
    result = {
        "vault": "dev",
        "total": 5,
        "changed": 2,
        "changed_keys": ["X", "Y"],
        "dry_run": True,
    }
    output = format_normalize_result(result)
    assert "dry run" in output
