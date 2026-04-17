import pytest
from unittest.mock import patch
from envault.cli_stats import cmd_stats


SAMPLE_STATS = {
    "total": 3,
    "empty": 0,
    "non_empty": 3,
    "avg_key_length": 6.0,
    "avg_value_length": 5.0,
    "longest_key": "DB_HOST",
    "shortest_key": "PORT",
    "prefixes": {"DB": 1},
}


@pytest.fixture
def mock_get_stats():
    with patch("envault.cli_stats.get_stats", return_value=SAMPLE_STATS) as m:
        yield m


def test_cmd_stats_ok(mock_get_stats):
    result = cmd_stats("myenv", "pw")
    assert result["ok"] is True
    assert result["stats"]["total"] == 3


def test_cmd_stats_includes_formatted_by_default(mock_get_stats):
    result = cmd_stats("myenv", "pw")
    assert "formatted" in result
    assert "Total keys" in result["formatted"]


def test_cmd_stats_raw_skips_formatted(mock_get_stats):
    result = cmd_stats("myenv", "pw", raw=True)
    assert "formatted" not in result


def test_cmd_stats_error_on_missing_vault():
    from envault.env_stats import StatsError
    with patch("envault.cli_stats.get_stats", side_effect=StatsError("vault not found")):
        result = cmd_stats("missing", "pw")
    assert result["ok"] is False
    assert "vault not found" in result["error"]


def test_cmd_stats_prefixes_present(mock_get_stats):
    result = cmd_stats("myenv", "pw")
    assert result["stats"]["prefixes"]["DB"] == 1
