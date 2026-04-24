"""Tests for envault.env_intersection."""

import pytest
from unittest.mock import patch
from envault.env_intersection import (
    IntersectionError,
    intersect_vaults,
    format_intersection_result,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "localhost", "DB_PORT": "5433", "APP_KEY": "xyz"}
ENV_C = {"DB_HOST": "localhost", "DB_PORT": "5432", "EXTRA": "1"}


def _make_deps(envs: dict[str, dict], existing: list[str] | None = None):
    """Return (mock_vault_exists, mock_get_env_vars) patch targets."""
    if existing is None:
        existing = list(envs.keys())

    def _exists(name):
        return name in existing

    def _get(name, password):
        return envs[name]

    return _exists, _get


@pytest.fixture()
def patched(request):
    envs = getattr(request, "param", {"a": ENV_A, "b": ENV_B})
    _exists, _get = _make_deps(envs)
    with patch("envault.env_intersection.vault_exists", side_effect=_exists), \
         patch("envault.env_intersection.get_env_vars", side_effect=_get):
        yield envs


# ---------------------------------------------------------------------------
# intersect_vaults
# ---------------------------------------------------------------------------

def test_intersect_requires_two_vaults():
    with pytest.raises(IntersectionError, match="At least two"):
        intersect_vaults(["only_one"], "pw")


def test_intersect_raises_if_vault_missing():
    with patch("envault.env_intersection.vault_exists", return_value=False):
        with pytest.raises(IntersectionError, match="Vault not found"):
            intersect_vaults(["a", "b"], "pw")


def test_intersect_returns_common_keys(patched):
    result = intersect_vaults(["a", "b"], "pw")
    assert set(result["common_keys"]) == {"DB_HOST", "DB_PORT"}


def test_intersect_total_common_count(patched):
    result = intersect_vaults(["a", "b"], "pw")
    assert result["total_common"] == 2


def test_intersect_vault_count(patched):
    result = intersect_vaults(["a", "b"], "pw")
    assert result["vault_count"] == 2


def test_intersect_common_keys_sorted(patched):
    result = intersect_vaults(["a", "b"], "pw")
    assert result["common_keys"] == sorted(result["common_keys"])


def test_intersect_values_must_match_filters_mismatched():
    envs = {"a": ENV_A, "b": ENV_B}
    _exists, _get = _make_deps(envs)
    with patch("envault.env_intersection.vault_exists", side_effect=_exists), \
         patch("envault.env_intersection.get_env_vars", side_effect=_get):
        result = intersect_vaults(["a", "b"], "pw", values_must_match=True)
    # DB_HOST matches; DB_PORT differs
    assert "DB_HOST" in result["common_pairs"]
    assert "DB_PORT" not in result["common_pairs"]


def test_intersect_three_vaults():
    envs = {"a": ENV_A, "b": ENV_B, "c": ENV_C}
    _exists, _get = _make_deps(envs)
    with patch("envault.env_intersection.vault_exists", side_effect=_exists), \
         patch("envault.env_intersection.get_env_vars", side_effect=_get):
        result = intersect_vaults(["a", "b", "c"], "pw")
    assert set(result["common_keys"]) == {"DB_HOST", "DB_PORT"}
    assert result["vault_count"] == 3


def test_intersect_no_common_keys():
    envs = {"a": {"ONLY_A": "1"}, "b": {"ONLY_B": "2"}}
    _exists, _get = _make_deps(envs)
    with patch("envault.env_intersection.vault_exists", side_effect=_exists), \
         patch("envault.env_intersection.get_env_vars", side_effect=_get):
        result = intersect_vaults(["a", "b"], "pw")
    assert result["common_keys"] == []
    assert result["total_common"] == 0


# ---------------------------------------------------------------------------
# format_intersection_result
# ---------------------------------------------------------------------------

def test_format_includes_vault_count():
    result = {"vault_count": 2, "total_common": 1, "common_keys": ["X"], "common_pairs": {}}
    out = format_intersection_result(result)
    assert "2" in out


def test_format_includes_key_names():
    result = {"vault_count": 2, "total_common": 2, "common_keys": ["A", "B"], "common_pairs": {}}
    out = format_intersection_result(result)
    assert "A" in out and "B" in out


def test_format_shows_matching_pairs():
    result = {
        "vault_count": 2,
        "total_common": 1,
        "common_keys": ["DB_HOST"],
        "common_pairs": {"DB_HOST": "localhost"},
    }
    out = format_intersection_result(result)
    assert "DB_HOST=localhost" in out
