"""Tests for envault/env_scope.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_scope import (
    ScopeError,
    clear_scope,
    filter_by_scope,
    format_scope_info,
    get_scope,
    set_scope,
)


@pytest.fixture
def mock_scope_deps():
    vault_data = {}

    def _exists(name):
        return name == "myvault"

    def _load(name, pw):
        return dict(vault_data)

    def _save(name, pw, data):
        vault_data.clear()
        vault_data.update(data)

    with (
        patch("envault.env_scope.vault_exists", side_effect=_exists),
        patch("envault.env_scope.load_vault", side_effect=_load),
        patch("envault.env_scope.save_vault", side_effect=_save),
    ):
        yield vault_data


def test_set_scope_returns_summary(mock_scope_deps):
    result = set_scope("myvault", "pw", "dev")
    assert result["vault"] == "myvault"
    assert result["scope"] == "dev"
    assert result["status"] == "ok"


def test_set_scope_persists(mock_scope_deps):
    set_scope("myvault", "pw", "staging")
    assert mock_scope_deps["__meta__"]["scope"] == "staging"


def test_set_scope_raises_if_vault_missing(mock_scope_deps):
    with pytest.raises(ScopeError, match="not found"):
        set_scope("nope", "pw", "dev")


def test_set_scope_raises_on_invalid_scope(mock_scope_deps):
    with pytest.raises(ScopeError, match="Invalid scope"):
        set_scope("myvault", "pw", "universe")


def test_get_scope_returns_none_when_unset(mock_scope_deps):
    result = get_scope("myvault", "pw")
    assert result is None


def test_get_scope_returns_set_scope(mock_scope_deps):
    mock_scope_deps["__meta__"] = {"scope": "prod"}
    result = get_scope("myvault", "pw")
    assert result == "prod"


def test_get_scope_raises_if_vault_missing(mock_scope_deps):
    with pytest.raises(ScopeError):
        get_scope("ghost", "pw")


def test_clear_scope_removes_scope(mock_scope_deps):
    mock_scope_deps["__meta__"] = {"scope": "test"}
    result = clear_scope("myvault", "pw")
    assert result["cleared"] is True
    assert mock_scope_deps.get("__meta__", {}).get("scope") is None


def test_clear_scope_noop_when_no_scope(mock_scope_deps):
    result = clear_scope("myvault", "pw")
    assert result["cleared"] is False


def test_filter_by_scope_returns_matching(mock_scope_deps):
    mock_scope_deps["__meta__"] = {"scope": "dev"}
    with patch("envault.env_scope.vault_exists", return_value=True):
        with patch("envault.env_scope.load_vault", return_value=dict(mock_scope_deps)):
            result = filter_by_scope(["myvault", "other"], "pw", "dev")
    assert "myvault" in result


def test_filter_by_scope_raises_on_invalid_scope(mock_scope_deps):
    with pytest.raises(ScopeError, match="Invalid scope"):
        filter_by_scope(["myvault"], "pw", "badscope")


def test_format_scope_info_with_scope():
    assert "dev" in format_scope_info("myvault", "dev")


def test_format_scope_info_no_scope():
    assert "no scope" in format_scope_info("myvault", None)
