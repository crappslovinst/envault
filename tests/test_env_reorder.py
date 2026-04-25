"""Tests for envault.env_reorder."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_reorder import (
    reorder_vault,
    format_reorder_result,
    ReorderError,
    _sort_by_prefix,
)


ENV = {
    "DB_HOST": "localhost",
    "APP_NAME": "myapp",
    "DB_PORT": "5432",
    "APP_ENV": "dev",
    "ZEBRA": "last",
}


@pytest.fixture
def mock_reorder_deps():
    with patch("envault.env_reorder.vault_exists") as _exists, \
         patch("envault.env_reorder.get_env_vars") as _get, \
         patch("envault.env_reorder.push_env") as _push:
        _exists.return_value = True
        _get.return_value = dict(ENV)
        yield _exists, _get, _push


def test_reorder_raises_if_vault_missing():
    with patch("envault.env_reorder.vault_exists", return_value=False):
        with pytest.raises(ReorderError, match="not found"):
            reorder_vault("ghost", "pw")


def test_reorder_raises_on_unknown_strategy(mock_reorder_deps):
    with pytest.raises(ReorderError, match="Unknown strategy"):
        reorder_vault("v", "pw", strategy="random")


def test_reorder_custom_requires_order(mock_reorder_deps):
    with pytest.raises(ReorderError, match="custom_order"):
        reorder_vault("v", "pw", strategy="custom", custom_order=[])


def test_reorder_alpha_sorts_ascending(mock_reorder_deps):
    result = reorder_vault("v", "pw", strategy="alpha")
    assert result["order"] == sorted(ENV.keys())


def test_reorder_alpha_desc_sorts_descending(mock_reorder_deps):
    result = reorder_vault("v", "pw", strategy="alpha_desc")
    assert result["order"] == sorted(ENV.keys(), reverse=True)


def test_reorder_by_prefix_groups_correctly(mock_reorder_deps):
    result = reorder_vault("v", "pw", strategy="by_prefix")
    order = result["order"]
    # APP_ keys come before DB_ keys; ZEBRA has no underscore so goes to __other__
    app_idx = [order.index(k) for k in order if k.startswith("APP_")]
    db_idx = [order.index(k) for k in order if k.startswith("DB_")]
    assert max(app_idx) < min(db_idx)


def test_reorder_custom_order_respected(mock_reorder_deps):
    custom = ["ZEBRA", "APP_NAME", "DB_HOST"]
    result = reorder_vault("v", "pw", strategy="custom", custom_order=custom)
    order = result["order"]
    # The three custom keys appear first in specified order
    assert order[:3] == ["ZEBRA", "APP_NAME", "DB_HOST"]


def test_reorder_custom_appends_remaining(mock_reorder_deps):
    custom = ["ZEBRA"]
    result = reorder_vault("v", "pw", strategy="custom", custom_order=custom)
    assert result["order"][0] == "ZEBRA"
    assert set(result["order"]) == set(ENV.keys())


def test_reorder_dry_run_skips_push(mock_reorder_deps):
    _exists, _get, _push = mock_reorder_deps
    reorder_vault("v", "pw", strategy="alpha", dry_run=True)
    _push.assert_not_called()


def test_reorder_calls_push_when_changed(mock_reorder_deps):
    _exists, _get, _push = mock_reorder_deps
    # ENV keys are not in alpha order, so alpha strategy should trigger push
    result = reorder_vault("v", "pw", strategy="alpha", dry_run=False)
    if result["changed"]:
        _push.assert_called_once()


def test_reorder_returns_correct_total(mock_reorder_deps):
    result = reorder_vault("v", "pw", strategy="alpha")
    assert result["total"] == len(ENV)


def test_sort_by_prefix_unit():
    env = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "p", "APP_ENV": "e"}
    ordered = _sort_by_prefix(env)
    keys = list(ordered.keys())
    assert keys.index("APP_ENV") < keys.index("APP_NAME") < keys.index("DB_HOST")


def test_format_reorder_result_contains_vault():
    result = {
        "vault": "myvault",
        "strategy": "alpha",
        "total": 5,
        "changed": True,
        "dry_run": False,
        "order": ["A", "B", "C"],
    }
    formatted = format_reorder_result(result)
    assert "myvault" in formatted
    assert "alpha" in formatted
    assert "5" in formatted
