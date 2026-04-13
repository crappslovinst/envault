"""Tests for envault/merge.py"""

import pytest
from envault.merge import merge_envs, get_conflicts, resolve_interactive


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}
INCOMING = {"DB_HOST": "prod.db", "DB_PORT": "5432", "NEW_KEY": "hello"}


def test_merge_theirs_overwrites_conflicts():
    result = merge_envs(BASE, INCOMING, strategy="theirs")
    assert result["DB_HOST"] == "prod.db"


def test_merge_theirs_keeps_base_only_keys():
    result = merge_envs(BASE, INCOMING, strategy="theirs")
    assert result["APP_ENV"] == "dev"


def test_merge_theirs_adds_new_keys():
    result = merge_envs(BASE, INCOMING, strategy="theirs")
    assert result["NEW_KEY"] == "hello"


def test_merge_ours_keeps_base_on_conflict():
    result = merge_envs(BASE, INCOMING, strategy="ours")
    assert result["DB_HOST"] == "localhost"


def test_merge_ours_still_adds_new_keys():
    result = merge_envs(BASE, INCOMING, strategy="ours")
    assert result["NEW_KEY"] == "hello"


def test_merge_unchanged_key_preserved():
    result = merge_envs(BASE, INCOMING, strategy="theirs")
    assert result["DB_PORT"] == "5432"


def test_merge_interactive_raises():
    with pytest.raises(NotImplementedError):
        merge_envs(BASE, INCOMING, strategy="interactive")


def test_get_conflicts_finds_changed_keys():
    conflicts = get_conflicts(BASE, INCOMING)
    assert "DB_HOST" in conflicts
    assert conflicts["DB_HOST"] == ("localhost", "prod.db")


def test_get_conflicts_ignores_same_values():
    conflicts = get_conflicts(BASE, INCOMING)
    assert "DB_PORT" not in conflicts


def test_get_conflicts_ignores_new_keys():
    conflicts = get_conflicts(BASE, INCOMING)
    assert "NEW_KEY" not in conflicts


def test_get_conflicts_empty_when_no_overlap():
    conflicts = get_conflicts({"A": "1"}, {"B": "2"})
    assert conflicts == {}


def test_resolve_interactive_applies_resolutions():
    resolutions = {"DB_HOST": "custom.db"}
    result = resolve_interactive(BASE, INCOMING, resolutions)
    assert result["DB_HOST"] == "custom.db"


def test_resolve_interactive_falls_back_to_theirs():
    resolutions = {}
    result = resolve_interactive(BASE, INCOMING, resolutions)
    assert result["DB_HOST"] == "prod.db"


def test_resolve_interactive_includes_all_keys():
    resolutions = {"DB_HOST": "manual.db"}
    result = resolve_interactive(BASE, INCOMING, resolutions)
    assert "APP_ENV" in result
    assert "NEW_KEY" in result
