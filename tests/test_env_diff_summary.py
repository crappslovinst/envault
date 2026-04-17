import pytest
from unittest.mock import patch
from envault.env_diff_summary import summarize_diff, format_summary, DiffSummaryError


ENV_A = {"KEY1": "val1", "KEY2": "old", "SHARED": "same"}
ENV_B = {"KEY1": "val1", "KEY2": "new", "SHARED": "same", "KEY3": "added"}


@pytest.fixture
def mock_get_env():
    def _get(vault, password):
        if vault == "a":
            return dict(ENV_A)
        if vault == "b":
            return dict(ENV_B)
        raise Exception("vault not found")

    with patch("envault.env_diff_summary.get_env_vars", side_effect=_get) as m:
        yield m


def test_summarize_diff_added(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert "KEY3" in result["added"]


def test_summarize_diff_removed(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert result["removed"] == []


def test_summarize_diff_changed(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert "KEY2" in result["changed"]


def test_summarize_diff_unchanged(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert "KEY1" in result["unchanged"]
    assert "SHARED" in result["unchanged"]


def test_summarize_diff_total(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert result["total_diff"] == len(result["added"]) + len(result["removed"]) + len(result["changed"])


def test_summarize_diff_vault_names(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    assert result["vault_a"] == "a"
    assert result["vault_b"] == "b"


def test_summarize_diff_raises_on_bad_vault_a():
    with patch("envault.env_diff_summary.get_env_vars", side_effect=Exception("missing")):
        with pytest.raises(DiffSummaryError, match="Cannot read vault 'x'"):
            summarize_diff("x", "b", "pass")


def test_summarize_diff_raises_on_bad_vault_b():
    def _get(vault, password):
        if vault == "a":
            return dict(ENV_A)
        raise Exception("missing")

    with patch("envault.env_diff_summary.get_env_vars", side_effect=_get):
        with pytest.raises(DiffSummaryError, match="Cannot read vault 'b'"):
            summarize_diff("a", "b", "pass")


def test_format_summary_contains_vault_names(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    text = format_summary(result)
    assert "a" in text
    assert "b" in text


def test_format_summary_shows_counts(mock_get_env):
    result = summarize_diff("a", "b", "pass")
    text = format_summary(result)
    assert "Added" in text
    assert "Changed" in text
    assert "Unchanged" in text
