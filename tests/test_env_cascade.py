"""Tests for env_cascade and cli_cascade modules."""

import pytest
from unittest.mock import patch

from envault.env_cascade import CascadeError, resolve_cascade, resolve_cascade_with_sources
from envault.cli_cascade import cmd_cascade, format_cascade_result


BASE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}
PROD_VARS = {"DB_HOST": "prod.db.internal", "SECRET_KEY": "s3cr3t"}


@pytest.fixture
def patched_cascade(tmp_path):
    with (
        patch("envault.env_cascade.vault_exists", return_value=True),
        patch("envault.env_cascade.get_env_vars") as mock_get,
    ):
        mock_get.side_effect = lambda name, pw: {
            "base": BASE_VARS,
            "prod": PROD_VARS,
        }.get(name, {})
        yield mock_get


def test_resolve_cascade_merges_in_order(patched_cascade):
    result = resolve_cascade(["base", "prod"], "pass")
    assert result["DB_HOST"] == "prod.db.internal"  # prod wins
    assert result["DB_PORT"] == "5432"              # only in base
    assert result["SECRET_KEY"] == "s3cr3t"         # only in prod


def test_resolve_cascade_single_vault(patched_cascade):
    result = resolve_cascade(["base"], "pass")
    assert result == BASE_VARS


def test_resolve_cascade_empty_list_raises():
    with pytest.raises(CascadeError, match="At least one"):
        resolve_cascade([], "pass")


def test_resolve_cascade_missing_vault_raises():
    with patch("envault.env_cascade.vault_exists", return_value=False):
        with pytest.raises(CascadeError, match="not found"):
            resolve_cascade(["ghost"], "pass")


def test_resolve_cascade_with_sources_tracks_origin(patched_cascade):
    result = resolve_cascade_with_sources(["base", "prod"], "pass")
    assert result["DB_HOST"]["source"] == "prod"
    assert result["DB_PORT"]["source"] == "base"
    assert result["SECRET_KEY"]["source"] == "prod"
    assert result["DB_HOST"]["value"] == "prod.db.internal"


def test_cmd_cascade_ok(patched_cascade):
    result = cmd_cascade(["base", "prod"], "pass")
    assert result["ok"] is True
    assert result["total"] == 4
    assert result["vars"]["DB_HOST"] == "prod.db.internal"


def test_cmd_cascade_with_sources(patched_cascade):
    result = cmd_cascade(["base", "prod"], "pass", show_sources=True)
    assert result["ok"] is True
    assert "sources" in result
    assert result["sources"]["DB_HOST"] == "prod"


def test_cmd_cascade_error_returns_ok_false():
    with patch("envault.env_cascade.vault_exists", return_value=False):
        result = cmd_cascade(["missing"], "pass")
    assert result["ok"] is False
    assert "error" in result


def test_format_cascade_result_includes_keys(patched_cascade):
    result = cmd_cascade(["base", "prod"], "pass", show_sources=True)
    output = format_cascade_result(result)
    assert "DB_HOST" in output
    assert "prod.db.internal" in output
    assert "from: prod" in output


def test_format_cascade_result_error():
    result = {"ok": False, "error": "Vault(s) not found: ghost"}
    output = format_cascade_result(result)
    assert "[error]" in output
    assert "ghost" in output
