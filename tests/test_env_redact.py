"""Tests for env_redact module."""

import pytest
from unittest.mock import patch
from envault.env_redact import redact_env, format_redact_result, count_redacted, RedactError, REDACTED


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "supersecret",
    "API_KEY": "abc123",
    "DEBUG": "true",
    "SECRET_TOKEN": "tok_xyz",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_redact.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_redact_hides_sensitive_keys(mock_get_env):
    result = redact_env("myapp", "pass")
    assert result["DB_PASSWORD"] == REDACTED
    assert result["API_KEY"] == REDACTED
    assert result["SECRET_TOKEN"] == REDACTED


def test_redact_keeps_non_sensitive_keys(mock_get_env):
    result = redact_env("myapp", "pass")
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"


def test_redact_show_keys_reveals_specific(mock_get_env):
    result = redact_env("myapp", "pass", show_keys=["API_KEY"])
    assert result["API_KEY"] == "abc123"
    assert result["DB_PASSWORD"] == REDACTED


def test_redact_raises_on_bad_vault():
    with patch("envault.env_redact.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(RedactError, match="not found"):
            redact_env("missing", "pass")


def test_count_redacted_correct(mock_get_env):
    result = redact_env("myapp", "pass")
    assert count_redacted(result) == 3


def test_count_redacted_with_show_keys(mock_get_env):
    result = redact_env("myapp", "pass", show_keys=["API_KEY", "DB_PASSWORD"])
    assert count_redacted(result) == 1  # only SECRET_TOKEN remains redacted


def test_format_redact_result_sorted():
    data = {"Z_KEY": "val", "A_KEY": REDACTED}
    out = format_redact_result(data)
    lines = out.splitlines()
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("Z_KEY")


def test_format_redact_result_empty():
    assert format_redact_result({}) == "(empty)"
