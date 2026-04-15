"""Tests for envault.cli_diff_watch."""

import pytest
from unittest.mock import patch
from envault.cli_diff_watch import cmd_snapshot_diff, cmd_watch_diff


SAMPLE_DIFF = [
    {"key": "DB_URL", "status": "changed", "old": "old", "new": "new"}
]


@pytest.fixture()
def mock_snapshot():
    with patch("envault.cli_diff_watch.snapshot_diff", return_value=SAMPLE_DIFF) as m:
        yield m


@pytest.fixture()
def mock_watch():
    with patch("envault.cli_diff_watch.watch_diff") as m:
        yield m


def test_cmd_snapshot_diff_ok(mock_snapshot):
    result = cmd_snapshot_diff("myapp", "pass", ".env")
    assert result["ok"] is True
    assert result["has_diff"] is True
    assert result["vault"] == "myapp"


def test_cmd_snapshot_diff_formatted_string(mock_snapshot):
    result = cmd_snapshot_diff("myapp", "pass", ".env")
    assert isinstance(result["formatted"], str)


def test_cmd_snapshot_diff_error():
    from envault.env_diff_watch import DiffWatchError
    with patch("envault.cli_diff_watch.snapshot_diff", side_effect=DiffWatchError("boom")):
        result = cmd_snapshot_diff("bad", "pass", ".env")
    assert result["ok"] is False
    assert "boom" in result["error"]


def test_cmd_watch_diff_ok(mock_watch):
    result = cmd_watch_diff("myapp", "pass", ".env", max_iterations=0)
    assert result["ok"] is True
    assert result["changes_detected"] == 0


def test_cmd_watch_diff_error():
    from envault.env_diff_watch import DiffWatchError
    with patch("envault.cli_diff_watch.watch_diff", side_effect=DiffWatchError("oops")):
        result = cmd_watch_diff("bad", "pass", ".env")
    assert result["ok"] is False
    assert "oops" in result["error"]


def test_cmd_watch_diff_quiet_suppresses_print(mock_watch, capsys):
    result = cmd_watch_diff("myapp", "pass", ".env", quiet=True, max_iterations=0)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert result["ok"] is True
