"""Tests for envault/env_merge_policy.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_merge_policy import (
    MergePolicyError,
    VALID_STRATEGIES,
    set_policy,
    get_policy,
    clear_policy,
)


@pytest.fixture
def mock_storage():
    store = {}

    def _exists(name):
        return name in store

    def _load(name, pwd):
        return store[name].copy()

    def _save(name, pwd, data):
        store[name] = data.copy()

    with (
        patch("envault.env_merge_policy.vault_exists", side_effect=_exists),
        patch("envault.env_merge_policy.load_vault", side_effect=_load),
        patch("envault.env_merge_policy.save_vault", side_effect=_save),
    ):
        store["myapp"] = {}
        yield store


def test_set_policy_returns_summary(mock_storage):
    result = set_policy("myapp", "pass", "ours")
    assert result["vault"] == "myapp"
    assert result["strategy"] == "ours"
    assert result["status"] == "ok"


def test_set_policy_persists(mock_storage):
    set_policy("myapp", "pass", "theirs")
    assert mock_storage["myapp"]["__meta__"]["__merge_policy__"] == "theirs"


def test_set_policy_invalid_strategy_raises(mock_storage):
    with pytest.raises(MergePolicyError, match="Invalid strategy"):
        set_policy("myapp", "pass", "banana")


def test_set_policy_raises_if_vault_missing(mock_storage):
    with pytest.raises(MergePolicyError, match="not found"):
        set_policy("ghost", "pass", "ours")


def test_get_policy_returns_set_value(mock_storage):
    set_policy("myapp", "pass", "prompt")
    result = get_policy("myapp", "pass")
    assert result == "prompt"


def test_get_policy_defaults_to_prompt(mock_storage):
    result = get_policy("myapp", "pass")
    assert result == "prompt"


def test_get_policy_raises_if_vault_missing(mock_storage):
    with pytest.raises(MergePolicyError, match="not found"):
        get_policy("ghost", "pass")


def test_clear_policy_removes_entry(mock_storage):
    set_policy("myapp", "pass", "ours")
    result = clear_policy("myapp", "pass")
    assert result["cleared"] is True
    assert "__merge_policy__" not in mock_storage["myapp"].get("__meta__", {})


def test_clear_policy_noop_if_not_set(mock_storage):
    result = clear_policy("myapp", "pass")
    assert result["cleared"] is False
    assert result["status"] == "ok"


def test_clear_policy_raises_if_vault_missing(mock_storage):
    with pytest.raises(MergePolicyError, match="not found"):
        clear_policy("ghost", "pass")


def test_all_valid_strategies_accepted(mock_storage):
    for strategy in VALID_STRATEGIES:
        result = set_policy("myapp", "pass", strategy)
        assert result["strategy"] == strategy
