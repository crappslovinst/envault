import pytest
from unittest.mock import patch
from envault.env_stats import get_stats, format_stats, StatsError


ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASS": "",
    "SECRET_KEY": "abc123",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_stats.get_env_vars", return_value=ENV) as m:
        yield m


def test_get_stats_total(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["total"] == 5


def test_get_stats_empty_count(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["empty"] == 1


def test_get_stats_non_empty_count(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["non_empty"] == 4


def test_get_stats_prefixes(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["prefixes"]["APP"] == 2
    assert s["prefixes"]["DB"] == 2


def test_get_stats_longest_key(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["longest_key"] == "SECRET_KEY"


def test_get_stats_shortest_key(mock_get_env):
    s = get_stats("myenv", "pw")
    assert s["shortest_key"] in ("APP_HOST", "APP_PORT", "DB_HOST", "DB_PASS")


def test_get_stats_empty_vault():
    with patch("envault.env_stats.get_env_vars", return_value={}):
        s = get_stats("empty", "pw")
    assert s["total"] == 0
    assert s["longest_key"] is None


def test_get_stats_raises_on_bad_vault():
    with patch("envault.env_stats.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(StatsError, match="not found"):
            get_stats("missing", "pw")


def test_format_stats_contains_total(mock_get_env):
    s = get_stats("myenv", "pw")
    out = format_stats(s)
    assert "Total keys" in out
    assert "5" in out


def test_format_stats_contains_prefixes(mock_get_env):
    s = get_stats("myenv", "pw")
    out = format_stats(s)
    assert "APP_*" in out
    assert "DB_*" in out
