"""Tests for envault.env_parser."""

import pytest
from envault.env_parser import parse_env, serialize_env


def test_parse_simple_pairs():
    content = "KEY=value\nFOO=bar"
    result = parse_env(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_skips_comments_and_blanks():
    content = "# comment\n\nKEY=value\n"
    result = parse_env(content)
    assert result == {"KEY": "value"}


def test_parse_double_quoted_value():
    result = parse_env('DB_URL="postgres://localhost/db"')
    assert result["DB_URL"] == "postgres://localhost/db"


def test_parse_single_quoted_value():
    result = parse_env("SECRET='my secret'")
    assert result["SECRET"] == "my secret"


def test_parse_inline_comment():
    result = parse_env("PORT=8080 # default port")
    assert result["PORT"] == "8080"


def test_parse_inline_comment_inside_quotes_preserved():
    result = parse_env('MSG="hello # world"')
    assert result["MSG"] == "hello # world"


def test_parse_ignores_lines_without_equals():
    content = "NODOC\nKEY=val"
    result = parse_env(content)
    assert "NODOC" not in result
    assert result["KEY"] == "val"


def test_serialize_simple():
    data = {"KEY": "value", "FOO": "bar"}
    text = serialize_env(data)
    reparsed = parse_env(text)
    assert reparsed == data


def test_serialize_quotes_values_with_spaces():
    data = {"GREETING": "hello world"}
    text = serialize_env(data)
    assert '"hello world"' in text


def test_serialize_empty_dict():
    assert serialize_env({}) == ""


def test_roundtrip_complex_env():
    original = (
        "# App config\n"
        "APP_NAME=envault\n"
        "DEBUG=false\n"
        'SECRET_KEY="s3cr3t!#key"\n'
        "PORT=5000 # http port\n"
    )
    parsed = parse_env(original)
    serialized = serialize_env(parsed)
    reparsed = parse_env(serialized)
    assert reparsed == parsed
