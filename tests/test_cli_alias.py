"""Tests for envault/cli_alias.py"""

from __future__ import annotations

import pytest

from envault.cli_alias import (
    cmd_list_aliases,
    cmd_remove_alias,
    cmd_resolve_alias,
    cmd_set_alias,
    format_alias_list,
)


@pytest.fixture()
def mock_alias_fns(monkeypatch):
    calls: dict[str, list] = {"set": [], "remove": [], "list": [], "resolve": []}

    def _set(vault, alias, pw):
        calls["set"].append((vault, alias))
        return {"vault": vault, "alias": alias, "action": "set"}

    def _remove(vault, alias, pw):
        calls["remove"].append((vault, alias))
        return {"vault": vault, "alias": alias, "action": "removed"}

    def _list(vault, pw):
        calls["list"].append(vault)
        return ["prod", "staging"]

    def _resolve(vault, alias, pw):
        calls["resolve"].append((vault, alias))
        return vault

    monkeypatch.setattr("envault.cli_alias.set_alias", _set)
    monkeypatch.setattr("envault.cli_alias.remove_alias", _remove)
    monkeypatch.setattr("envault.cli_alias.list_aliases", _list)
    monkeypatch.setattr("envault.cli_alias.resolve_alias", _resolve)
    return calls


def test_cmd_set_alias_returns_ok(mock_alias_fns):
    result = cmd_set_alias("myapp", "prod", "secret")
    assert result["ok"] is True
    assert "prod" in result["message"]


def test_cmd_set_alias_error(monkeypatch):
    from envault.alias import AliasError
    monkeypatch.setattr("envault.cli_alias.set_alias", lambda *a: (_ for _ in ()).throw(AliasError("oops")))
    result = cmd_set_alias("ghost", "x", "pw")
    assert result["ok"] is False
    assert "oops" in result["error"]


def test_cmd_remove_alias_returns_ok(mock_alias_fns):
    result = cmd_remove_alias("myapp", "prod", "secret")
    assert result["ok"] is True
    assert mock_alias_fns["remove"] == [("myapp", "prod")]


def test_cmd_list_aliases_returns_count(mock_alias_fns):
    result = cmd_list_aliases("myapp", "secret")
    assert result["ok"] is True
    assert result["count"] == 2
    assert "prod" in result["aliases"]


def test_cmd_resolve_alias_returns_target(mock_alias_fns):
    result = cmd_resolve_alias("myapp", "prod", "secret")
    assert result["ok"] is True
    assert result["resolves_to"] == "myapp"


def test_format_alias_list_empty():
    result = {"ok": True, "vault": "myapp", "aliases": []}
    output = format_alias_list(result)
    assert "No aliases" in output


def test_format_alias_list_with_aliases():
    result = {"ok": True, "vault": "myapp", "aliases": ["prod", "dev"]}
    output = format_alias_list(result)
    assert "prod" in output
    assert "dev" in output


def test_format_alias_list_error():
    result = {"ok": False, "error": "Vault not found"}
    output = format_alias_list(result)
    assert "Error" in output
