from unittest.mock import patch
from envault.cli_resolve import cmd_resolve, cmd_find_refs

BASE_ENV = {
    "HOST": "localhost",
    "DB_URL": "postgres://${HOST}/db",
}

RESOLVED_ENV = {
    "HOST": "localhost",
    "DB_URL": "postgres://localhost/db",
}


@patch("envault.cli_resolve.resolve_vars", return_value=RESOLVED_ENV)
@patch("envault.cli_resolve.get_env_vars", return_value=BASE_ENV)
def test_cmd_resolve_ok(mock_get, mock_resolve):
    result = cmd_resolve("myvault", "pass")
    assert result["ok"] is True
    assert result["resolved"]["DB_URL"] == "postgres://localhost/db"


@patch("envault.cli_resolve.resolve_vars", return_value=RESOLVED_ENV)
@patch("envault.cli_resolve.get_env_vars", return_value=BASE_ENV)
def test_cmd_resolve_includes_formatted(mock_get, mock_resolve):
    result = cmd_resolve("myvault", "pass")
    assert "formatted" in result
    assert isinstance(result["formatted"], str)


@patch("envault.cli_resolve.resolve_vars", return_value=RESOLVED_ENV)
@patch("envault.cli_resolve.get_env_vars", return_value=BASE_ENV)
def test_cmd_resolve_show_refs(mock_get, mock_resolve):
    result = cmd_resolve("myvault", "pass", show_refs=True)
    assert "references" in result


@patch("envault.cli_resolve.resolve_vars", side_effect=Exception("bad"))
@patch("envault.cli_resolve.get_env_vars", return_value=BASE_ENV)
def test_cmd_resolve_error(mock_get, mock_resolve):
    result = cmd_resolve("myvault", "pass")
    assert result["ok"] is False
    assert "error" in result


@patch("envault.cli_resolve.get_env_vars", return_value=BASE_ENV)
def test_cmd_find_refs_ok(mock_get):
    result = cmd_find_refs("myvault", "pass")
    assert result["ok"] is True
    assert "DB_URL" in result["references"]
    assert result["count"] == 1


@patch("envault.cli_resolve.get_env_vars", side_effect=Exception("missing"))
def test_cmd_find_refs_error(mock_get):
    result = cmd_find_refs("missing", "pass")
    assert result["ok"] is False
