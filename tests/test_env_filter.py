"""Tests for envault.env_filter."""

import pytest
from unittest.mock import patch
from envault.env_filter import FilterError, filter_env, format_filter_result

SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envault",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_filter.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_filter_by_prefix(mock_get_env):
    result = filter_env("myvault", "pass", prefix="DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_suffix(mock_get_env):
    result = filter_env("myvault", "pass", suffix="_KEY")
    assert set(result.keys()) == {"SECRET_KEY"}


def test_filter_by_pattern(mock_get_env):
    result = filter_env("myvault", "pass", pattern=r"^APP_")
    assert set(result.keys()) == {"APP_NAME", "APP_DEBUG"}


def test_filter_invert(mock_get_env):
    result = filter_env("myvault", "pass", prefix="DB_", invert=True)
    assert "DB_HOST" not in result
    assert "APP_NAME" in result


def test_filter_combined_prefix_and_suffix(mock_get_env):
    result = filter_env("myvault", "pass", prefix="APP_", suffix="_DEBUG")
    assert set(result.keys()) == {"APP_DEBUG"}


def test_filter_no_criteria_raises(mock_get_env):
    with pytest.raises(FilterError, match="At least one"):
        filter_env("myvault", "pass")


def test_filter_invalid_pattern_raises(mock_get_env):
    with pytest.raises(FilterError, match="Invalid regex"):
        filter_env("myvault", "pass", pattern="[invalid")


def test_filter_raises_on_bad_vault():
    with patch("envault.env_filter.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(FilterError, match="not found"):
            filter_env("missing", "pass", prefix="X")


def test_format_filter_result():
    filtered = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    out = format_filter_result(filtered, 5)
    assert "Matched 2 of 5" in out
    assert "DB_HOST=localhost" in out
    assert "DB_PORT=5432" in out
