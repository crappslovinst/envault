"""Tests for envault.env_numeric."""

import pytest
from unittest.mock import patch

from envault.env_numeric import NumericError, analyze_numeric, format_numeric_result


@pytest.fixture
def mock_get_env():
    with patch("envault.env_numeric.get_env_vars") as m:
        yield m


def test_analyze_numeric_returns_correct_keys(mock_get_env):
    mock_get_env.return_value = {"PORT": "8080", "TIMEOUT": "30", "NAME": "app"}
    result = analyze_numeric("myvault", "pass")
    assert set(result["numeric_keys"]) == {"PORT", "TIMEOUT"}
    assert result["count"] == 2


def test_analyze_numeric_sum(mock_get_env):
    mock_get_env.return_value = {"A": "10", "B": "20", "C": "30"}
    result = analyze_numeric("v", "p")
    assert result["sum"] == 60.0


def test_analyze_numeric_min_max(mock_get_env):
    mock_get_env.return_value = {"A": "5", "B": "100", "C": "50"}
    result = analyze_numeric("v", "p")
    assert result["min"] == 5.0
    assert result["max"] == 100.0


def test_analyze_numeric_average(mock_get_env):
    mock_get_env.return_value = {"X": "10", "Y": "20"}
    result = analyze_numeric("v", "p")
    assert result["average"] == 15.0


def test_analyze_numeric_no_numeric_values(mock_get_env):
    mock_get_env.return_value = {"NAME": "app", "ENV": "prod"}
    result = analyze_numeric("v", "p")
    assert result["count"] == 0
    assert result["sum"] is None
    assert result["min"] is None
    assert result["max"] is None
    assert result["average"] is None


def test_analyze_numeric_with_prefix(mock_get_env):
    mock_get_env.return_value = {"DB_PORT": "5432", "DB_MAX": "100", "APP_PORT": "8080"}
    result = analyze_numeric("v", "p", prefix="DB_")
    assert set(result["numeric_keys"]) == {"DB_PORT", "DB_MAX"}
    assert result["count"] == 2


def test_analyze_numeric_raises_on_bad_vault(mock_get_env):
    mock_get_env.side_effect = Exception("vault not found")
    with pytest.raises(NumericError, match="vault not found"):
        analyze_numeric("missing", "wrong")


def test_format_numeric_result_no_values():
    result = {
        "vault": "v", "prefix": None, "numeric_keys": [],
        "count": 0, "sum": None, "min": None, "max": None, "average": None,
    }
    out = format_numeric_result(result)
    assert "No numeric values" in out


def test_format_numeric_result_has_stats(mock_get_env):
    mock_get_env.return_value = {"A": "1", "B": "3"}
    result = analyze_numeric("v", "p")
    out = format_numeric_result(result)
    assert "sum" in out
    assert "average" in out
    assert "min" in out
    assert "max" in out
