import pytest
from unittest.mock import patch
from envault.env_placeholder import find_placeholders, replace_placeholders, format_placeholder_report, PlaceholderError
from envault.cli_placeholder import cmd_find_placeholders, cmd_replace_placeholders

FAKE_ENV = {
    "API_KEY": "CHANGE_ME",
    "DB_HOST": "localhost",
    "SECRET": "YOUR_SECRET_HERE",
    "PORT": "5432",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_placeholder.get_env_vars", return_value=FAKE_ENV) as m:
        yield m


def test_find_placeholders_detects_defaults(mock_get_env):
    hits = find_placeholders("dev", "pass")
    assert "API_KEY" in hits
    assert "SECRET" in hits
    assert "DB_HOST" not in hits
    assert "PORT" not in hits


def test_find_placeholders_custom_pattern(mock_get_env):
    hits = find_placeholders("dev", "pass", patterns=["localhost"])
    assert "DB_HOST" in hits
    assert "API_KEY" not in hits


def test_find_placeholders_no_hits(mock_get_env):
    hits = find_placeholders("dev", "pass", patterns=["NOPE"])
    assert hits == {}


def test_find_placeholders_raises_on_bad_vault():
    with patch("envault.env_placeholder.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(PlaceholderError, match="not found"):
            find_placeholders("missing", "pass")


def test_format_placeholder_report_empty():
    assert format_placeholder_report({}) == "No placeholders found."


def test_format_placeholder_report_with_hits():
    report = format_placeholder_report({"API_KEY": "CHANGE_ME"})
    assert "API_KEY" in report
    assert "CHANGE_ME" in report


def test_replace_placeholders_calls_push(mock_get_env):
    with patch("envault.env_placeholder.push_env") as mock_push:
        result = replace_placeholders("dev", "pass", {"API_KEY": "real-key"})
        assert result["replaced"] == ["API_KEY"]
        assert result["total"] == 1
        mock_push.assert_called_once()
        _, _, pushed_env = mock_push.call_args[0]
        assert pushed_env["API_KEY"] == "real-key"
        assert pushed_env["DB_HOST"] == "localhost"


def test_cmd_find_placeholders_ok(mock_get_env):
    result = cmd_find_placeholders("dev", "pass")
    assert result["ok"] is True
    assert "placeholders" in result
    assert "formatted" in result


def test_cmd_find_placeholders_error():
    with patch("envault.env_placeholder.get_env_vars", side_effect=Exception("boom")):
        result = cmd_find_placeholders("dev", "pass")
        assert result["ok"] is False
        assert "boom" in result["error"]


def test_cmd_replace_placeholders_no_replacements():
    result = cmd_replace_placeholders("dev", "pass", {})
    assert result["ok"] is False


def test_cmd_replace_placeholders_ok(mock_get_env):
    with patch("envault.env_placeholder.push_env"):
        result = cmd_replace_placeholders("dev", "pass", {"API_KEY": "real"})
        assert result["ok"] is True
        assert result["total"] == 1
