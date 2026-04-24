"""Tests for envault.cli_summarize."""

import pytest
from unittest.mock import patch

from envault.cli_summarize import cmd_summarize
from envault.env_summarize import SummarizeError


FAKE_RESULT = {
    "vault": "prod",
    "total": 5,
    "empty": 1,
    "non_empty": 4,
    "sensitive": 2,
    "top_prefixes": {"DB": 3},
}


@pytest.fixture
def mock_summarize():
    with patch(
        "envault.cli_summarize.summarize_vault", return_value=dict(FAKE_RESULT)
    ) as m:
        yield m


def test_cmd_summarize_ok(mock_summarize):
    result = cmd_summarize("prod", "pw")
    assert result["vault"] == "prod"
    assert result["total"] == 5


def test_cmd_summarize_includes_formatted_by_default(mock_summarize):
    result = cmd_summarize("prod", "pw")
    assert "formatted" in result
    assert isinstance(result["formatted"], str)


def test_cmd_summarize_raw_skips_formatted(mock_summarize):
    result = cmd_summarize("prod", "pw", raw=True)
    assert "formatted" not in result


def test_cmd_summarize_error_on_missing_vault():
    with patch(
        "envault.cli_summarize.summarize_vault",
        side_effect=SummarizeError("vault not found"),
    ):
        with pytest.raises(SummarizeError, match="vault not found"):
            cmd_summarize("missing", "pw")


def test_cmd_summarize_passes_credentials(mock_summarize):
    cmd_summarize("prod", "mypassword")
    mock_summarize.assert_called_once_with("prod", "mypassword")
