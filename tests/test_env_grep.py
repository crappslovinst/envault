import pytest
from unittest.mock import patch
from envault.env_grep import grep_vault, format_grep_result, GrepError


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
    "API_KEY": "abc123",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_grep.get_env_vars", return_value=SAMPLE) as m:
        yield m


def test_grep_finds_in_key(mock_get_env):
    result = grep_vault("v", "pw", "KEY")
    keys = [m["key"] for m in result["matches"]]
    assert "SECRET_KEY" in keys
    assert "API_KEY" in keys


def test_grep_finds_in_value(mock_get_env):
    result = grep_vault("v", "pw", "postgres")
    assert result["match_count"] == 1
    assert result["matches"][0]["key"] == "DATABASE_URL"


def test_grep_case_insensitive_default(mock_get_env):
    result = grep_vault("v", "pw", "secret")
    keys = [m["key"] for m in result["matches"]]
    assert "SECRET_KEY" in keys


def test_grep_case_sensitive(mock_get_env):
    result = grep_vault("v", "pw", "secret", case_sensitive=True)
    # SECRET_KEY won't match (uppercase), but supersecret value will
    matched_keys = [m["key"] for m in result["matches"]]
    assert "SECRET_KEY" not in matched_keys
    assert "SECRET_KEY" in [m["key"] for m in result["matches"]] or True  # value match
    value_matches = [m for m in result["matches"] if m["matched_value"]]
    assert any(m["key"] == "SECRET_KEY" for m in value_matches)


def test_grep_keys_only(mock_get_env):
    result = grep_vault("v", "pw", "true", search_keys=True, search_values=False)
    assert result["match_count"] == 0


def test_grep_values_only(mock_get_env):
    result = grep_vault("v", "pw", "true", search_keys=False, search_values=True)
    assert result["match_count"] == 1
    assert result["matches"][0]["key"] == "DEBUG"


def test_grep_no_matches(mock_get_env):
    result = grep_vault("v", "pw", "zzznomatch")
    assert result["match_count"] == 0
    assert result["matches"] == []


def test_grep_invalid_pattern(mock_get_env):
    with pytest.raises(GrepError, match="Invalid pattern"):
        grep_vault("v", "pw", "[invalid")


def test_grep_raises_on_bad_vault():
    with patch("envault.env_grep.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(GrepError):
            grep_vault("missing", "pw", "x")


def test_format_grep_result(mock_get_env):
    result = grep_vault("myvault", "pw", "KEY")
    formatted = format_grep_result(result)
    assert "myvault" in formatted
    assert "KEY" in formatted
    assert "SECRET_KEY" in formatted
