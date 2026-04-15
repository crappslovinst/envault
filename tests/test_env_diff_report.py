"""Tests for envault.env_diff_report and envault.cli_env_diff_report."""

import pytest
from unittest.mock import patch, mock_open

from envault.env_diff_report import generate_report, save_report, ReportError
from envault.cli_env_diff_report import cmd_diff_report, format_report_summary


VAULT_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
LOCAL_CONTENT = "DB_HOST=localhost\nDB_PORT=9999\nNEW_KEY=hello\n"


@pytest.fixture
def mock_deps():
    with patch("envault.env_diff_report.get_env_vars", return_value=VAULT_VARS) as mock_get, \
         patch("builtins.open", mock_open(read_data=LOCAL_CONTENT)):
        yield mock_get


def test_generate_report_has_diff(mock_deps):
    report = generate_report("myapp", "pass", ".env")
    assert report["has_diff"] is True


def test_generate_report_detects_changed(mock_deps):
    report = generate_report("myapp", "pass", ".env")
    assert "DB_PORT" in report["changed"]


def test_generate_report_detects_added(mock_deps):
    report = generate_report("myapp", "pass", ".env")
    assert "NEW_KEY" in report["added"]


def test_generate_report_detects_removed(mock_deps):
    report = generate_report("myapp", "pass", ".env")
    assert "SECRET" in report["removed"]


def test_generate_report_unchanged(mock_deps):
    report = generate_report("myapp", "pass", ".env")
    assert "DB_HOST" in report["unchanged"]


def test_generate_report_raises_on_bad_vault():
    with patch("envault.env_diff_report.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(ReportError, match="Failed to load vault"):
            generate_report("missing", "pass", ".env")


def test_generate_report_raises_on_missing_file():
    with patch("envault.env_diff_report.get_env_vars", return_value=VAULT_VARS), \
         patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(ReportError, match="not found"):
            generate_report("myapp", "pass", ".env")


def test_save_report_writes_file(mock_deps, tmp_path):
    report = generate_report("myapp", "pass", ".env")
    out = tmp_path / "report.txt"
    with patch("builtins.open", mock_open()) as mo:
        save_report(report, str(out))
        mo.assert_called_once_with(str(out), "w")


def test_cmd_diff_report_returns_counts(mock_deps):
    result = cmd_diff_report("myapp", "pass", ".env")
    assert result["changed"] == 1
    assert result["added"] == 1
    assert result["removed"] == 1
    assert result["unchanged"] == 1


def test_cmd_diff_report_hides_unchanged_by_default(mock_deps):
    result = cmd_diff_report("myapp", "pass", ".env", show_unchanged=False)
    for line in result["lines"]:
        assert not line.startswith(" "), f"Unexpected unchanged line: {line!r}"


def test_cmd_diff_report_shows_unchanged_when_requested(mock_deps):
    result = cmd_diff_report("myapp", "pass", ".env", show_unchanged=True)
    unchanged_lines = [l for l in result["lines"] if l.startswith(" ")]
    assert len(unchanged_lines) >= 1


def test_format_report_summary_contains_vault(mock_deps):
    result = cmd_diff_report("myapp", "pass", ".env")
    summary = format_report_summary(result)
    assert "myapp" in summary
    assert "Added" in summary
    assert "Removed" in summary
