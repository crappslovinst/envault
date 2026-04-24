"""Tests for envault/env_union.py"""

import pytest
from unittest.mock import patch
from envault.env_union import union_vaults, format_union_result, UnionError


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_deps(envs: dict[str, dict], existing: list[str] | None = None):
    """Patch vault_exists and get_env_vars for the given vault map."""
    if existing is None:
        existing = list(envs.keys())

    def _exists(name):
        return name in existing

    def _get(name, password):
        return envs[name]

    return (
        patch("envault.env_union.vault_exists", side_effect=_exists),
        patch("envault.env_union.get_env_vars", side_effect=_get),
    )


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_union_requires_two_vaults():
    with pytest.raises(UnionError, match="at least two"):
        union_vaults(["only_one"], "pass")


def test_union_raises_on_unknown_strategy():
    p1, p2 = _make_deps({"a": {}, "b": {}})
    with p1, p2:
        with pytest.raises(UnionError, match="unknown strategy"):
            union_vaults(["a", "b"], "pass", strategy="random")


def test_union_raises_if_vault_missing():
    p1, p2 = _make_deps({"a": {"X": "1"}}, existing=["a"])
    with p1, p2:
        with pytest.raises(UnionError, match="vault not found: b"):
            union_vaults(["a", "b"], "pass")


def test_union_merges_disjoint_vaults():
    envs = {"a": {"FOO": "1", "BAR": "2"}, "b": {"BAZ": "3"}}
    p1, p2 = _make_deps(envs)
    with p1, p2:
        result = union_vaults(["a", "b"], "pass")
    assert result["total"] == 3
    assert result["merged"] == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert result["conflict_count"] == 0


def test_union_first_strategy_keeps_first_value():
    envs = {"a": {"KEY": "from_a"}, "b": {"KEY": "from_b"}}
    p1, p2 = _make_deps(envs)
    with p1, p2:
        result = union_vaults(["a", "b"], "pass", strategy="first")
    assert result["merged"]["KEY"] == "from_a"
    assert result["conflict_count"] == 1


def test_union_last_strategy_keeps_last_value():
    envs = {"a": {"KEY": "from_a"}, "b": {"KEY": "from_b"}}
    p1, p2 = _make_deps(envs)
    with p1, p2:
        result = union_vaults(["a", "b"], "pass", strategy="last")
    assert result["merged"]["KEY"] == "from_b"


def test_union_conflict_lists_all_contributing_vaults():
    envs = {"a": {"K": "1"}, "b": {"K": "2"}, "c": {"K": "3"}}
    p1, p2 = _make_deps(envs)
    with p1, p2:
        result = union_vaults(["a", "b", "c"], "pass")
    assert set(result["conflicts"]["K"]) == {"a", "b", "c"}


def test_format_union_result_includes_summary():
    envs = {"x": {"A": "1"}, "y": {"A": "2", "B": "3"}}
    p1, p2 = _make_deps(envs)
    with p1, p2:
        result = union_vaults(["x", "y"], "pass")
    text = format_union_result(result)
    assert "Union of 2 vaults" in text
    assert "Total keys" in text
    assert "Conflicts" in text
    assert "A" in text
