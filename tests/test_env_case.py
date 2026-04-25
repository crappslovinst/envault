"""Tests for envault/env_case.py"""

from unittest.mock import patch
import pytest

from envault.env_case import CaseError, analyze_case, format_case_result, _classify


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_deps(exists: bool, env: dict):
    exists_patch = patch("envault.env_case.vault_exists", return_value=exists)
    get_patch = patch("envault.env_case.get_env_vars", return_value=env)
    return exists_patch, get_patch


# ---------------------------------------------------------------------------
# _classify
# ---------------------------------------------------------------------------

def test_classify_upper():
    assert _classify("DB_HOST") == "upper"


def test_classify_lower():
    assert _classify("db_host") == "lower"


def test_classify_mixed():
    assert _classify("DbHost") == "mixed"


# ---------------------------------------------------------------------------
# analyze_case
# ---------------------------------------------------------------------------

def test_analyze_raises_if_vault_missing():
    ep, gp = _make_deps(False, {})
    with ep, gp:
        with pytest.raises(CaseError, match="not found"):
            analyze_case("ghost", "pw")


def test_analyze_all_upper_no_inconsistencies():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_KEY": "abc"}
    ep, gp = _make_deps(True, env)
    with ep, gp:
        result = analyze_case("myapp", "pw")
    assert result["dominant_style"] == "upper"
    assert result["inconsistent_count"] == 0
    assert result["inconsistent"] == []


def test_analyze_detects_inconsistent_keys():
    env = {"DB_HOST": "x", "DB_PORT": "y", "db_user": "z"}
    ep, gp = _make_deps(True, env)
    with ep, gp:
        result = analyze_case("myapp", "pw")
    assert result["dominant_style"] == "upper"
    assert "db_user" in result["inconsistent"]
    assert result["inconsistent_count"] == 1


def test_analyze_total_matches_env_size():
    env = {"A": "1", "B": "2", "c": "3"}
    ep, gp = _make_deps(True, env)
    with ep, gp:
        result = analyze_case("v", "pw")
    assert result["total"] == 3


def test_analyze_groups_contain_all_keys():
    env = {"UPPER_KEY": "1", "lower_key": "2"}
    ep, gp = _make_deps(True, env)
    with ep, gp:
        result = analyze_case("v", "pw")
    all_grouped = [k for keys in result["groups"].values() for k in keys]
    assert sorted(all_grouped) == sorted(env.keys())


# ---------------------------------------------------------------------------
# format_case_result
# ---------------------------------------------------------------------------

def test_format_includes_vault_name():
    result = {
        "vault": "prod",
        "total": 5,
        "dominant_style": "upper",
        "inconsistent_count": 1,
        "inconsistent": ["bad_key"],
        "groups": {},
    }
    out = format_case_result(result)
    assert "prod" in out
    assert "upper" in out
    assert "bad_key" in out


def test_format_no_offending_section_when_clean():
    result = {
        "vault": "dev",
        "total": 2,
        "dominant_style": "upper",
        "inconsistent_count": 0,
        "inconsistent": [],
        "groups": {},
    }
    out = format_case_result(result)
    assert "Offending" not in out
