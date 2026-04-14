"""Tests for envault/alias.py"""

from __future__ import annotations

import pytest

from envault.alias import AliasError, list_aliases, remove_alias, resolve_alias, set_alias


@pytest.fixture()
def mock_alias_deps(monkeypatch):
    """Patch storage layer with an in-memory vault store."""
    store: dict[str, dict] = {}

    def _exists(name):
        return name in store

    def _load(name, password):
        return dict(store[name])

    def _save(name, data, password):
        store[name] = dict(data)

    monkeypatch.setattr("envault.alias.vault_exists", _exists)
    monkeypatch.setattr("envault.alias.load_vault", _load)
    monkeypatch.setattr("envault.alias.save_vault", _save)
    return store


def test_set_alias_returns_summary(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    result = set_alias("myapp", "prod", "secret")
    assert result["alias"] == "prod"
    assert result["vault"] == "myapp"
    assert result["action"] == "set"


def test_set_alias_persists(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    set_alias("myapp", "prod", "secret")
    aliases = list_aliases("myapp", "secret")
    assert "prod" in aliases


def test_set_alias_raises_if_vault_missing(mock_alias_deps):
    with pytest.raises(AliasError, match="not found"):
        set_alias("ghost", "prod", "secret")


def test_set_alias_raises_on_invalid_name(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    with pytest.raises(AliasError, match="Invalid alias"):
        set_alias("myapp", "bad-alias!", "secret")


def test_remove_alias_removes_it(mock_alias_deps):
    mock_alias_deps["myapp"] = {"_meta": {"aliases": {"prod": "myapp"}}}
    remove_alias("myapp", "prod", "secret")
    aliases = list_aliases("myapp", "secret")
    assert "prod" not in aliases


def test_remove_alias_raises_if_not_found(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    with pytest.raises(AliasError, match="not found"):
        remove_alias("myapp", "nonexistent", "secret")


def test_list_aliases_empty_by_default(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    assert list_aliases("myapp", "secret") == []


def test_list_aliases_returns_all(mock_alias_deps):
    mock_alias_deps["myapp"] = {"_meta": {"aliases": {"dev": "myapp", "staging": "myapp"}}}
    aliases = list_aliases("myapp", "secret")
    assert set(aliases) == {"dev", "staging"}


def test_resolve_alias_returns_vault_name(mock_alias_deps):
    mock_alias_deps["myapp"] = {"_meta": {"aliases": {"live": "myapp"}}}
    assert resolve_alias("myapp", "live", "secret") == "myapp"


def test_resolve_alias_raises_if_missing(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    with pytest.raises(AliasError, match="not found"):
        resolve_alias("myapp", "nope", "secret")


def test_multiple_aliases_coexist(mock_alias_deps):
    mock_alias_deps["myapp"] = {}
    set_alias("myapp", "alpha", "secret")
    set_alias("myapp", "beta", "secret")
    aliases = list_aliases("myapp", "secret")
    assert "alpha" in aliases
    assert "beta" in aliases
