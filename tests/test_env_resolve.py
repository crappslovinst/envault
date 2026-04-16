import pytest
from unittest.mock import patch
from envault.env_resolve import (
    resolve_vars,
    find_references,
    _interpolate,
    format_resolve_result,
    ResolveError,
)

BASE_ENV = {
    "HOST": "localhost",
    "PORT": "5432",
    "DB_URL": "postgres://${HOST}:${PORT}/mydb",
    "APP_URL": "http://${HOST}",
}


def _make_get(env):
    return lambda vault, password: dict(env)


@patch("envault.env_resolve.get_env_vars", side_effect=_make_get(BASE_ENV))
def test_resolve_interpolates_refs(mock_get):
    result = resolve_vars("myvault", "pass")
    assert result["DB_URL"] == "postgres://localhost:5432/mydb"
    assert result["APP_URL"] == "http://localhost"


@patch("envault.env_resolve.get_env_vars", side_effect=_make_get(BASE_ENV))
def test_resolve_leaves_plain_values(mock_get):
    result = resolve_vars("myvault", "pass")
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


@patch("envault.env_resolve.get_env_vars", side_effect=lambda v, p: (_ for _ in ()).throw(Exception("not found")))
def test_resolve_raises_on_bad_vault(mock_get):
    with pytest.raises(ResolveError):
        resolve_vars("missing", "pass")


def test_interpolate_replaces_known_key():
    env = {"NAME": "world"}
    assert _interpolate("hello_${NAME}", env) == "hello_world"


def test_interpolate_leaves_unknown_key():
    assert _interpolate("${UNKNOWN}", {}) == "${UNKNOWN}"


def test_find_references_detects_refs():
    env = {"A": "${B}_suffix", "B": "plain"}
    refs = find_references(env)
    assert refs == {"A": ["B"]}


def test_find_references_empty_when_no_refs():
    env = {"A": "hello", "B": "world"}
    assert find_references(env) == {}


def test_format_resolve_result_shows_changes():
    original = {"URL": "http://${HOST}"}
    resolved = {"URL": "http://localhost"}
    out = format_resolve_result(resolved, original)
    assert "URL" in out
    assert "localhost" in out


def test_format_resolve_result_no_changes():
    env = {"A": "plain"}
    out = format_resolve_result(env, env)
    assert "No interpolations" in out


@patch("envault.env_resolve.get_env_vars")
def test_resolve_chained_refs(mock_get):
    mock_get.return_value = {
        "A": "hello",
        "B": "${A}_world",
        "C": "${B}!",
    }
    result = resolve_vars("v", "p")
    assert result["C"] == "hello_world!"
