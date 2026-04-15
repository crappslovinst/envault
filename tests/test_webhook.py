"""Tests for envault/webhook.py and envault/cli_webhook.py."""

import pytest
from unittest.mock import patch, MagicMock

from envault.webhook import set_webhook, remove_webhook, list_webhooks, fire_webhook, WebhookError
from envault.cli_webhook import cmd_set_webhook, cmd_remove_webhook, cmd_list_webhooks, format_webhook_list


VAULT = "myproject"
PASS = "secret"


@pytest.fixture
def mock_webhook_deps(tmp_path):
    base_vault = {"DB_HOST": "localhost"}
    saved = {}

    def _exists(name):
        return name in saved or name == VAULT

    def _load(name, pw):
        return saved.get(name, dict(base_vault))

    def _save(name, pw, data):
        saved[name] = data

    with patch("envault.webhook.vault_exists", side_effect=_exists), \
         patch("envault.webhook.load_vault", side_effect=_load), \
         patch("envault.webhook.save_vault", side_effect=_save):
        yield saved


def test_set_webhook_returns_summary(mock_webhook_deps):
    result = set_webhook(VAULT, PASS, "push", "https://example.com/hook")
    assert result["event"] == "push"
    assert result["url"] == "https://example.com/hook"
    assert result["status"] == "registered"


def test_set_webhook_persists(mock_webhook_deps):
    set_webhook(VAULT, PASS, "pull", "https://hooks.example.com/pull")
    hooks = list_webhooks(VAULT, PASS)
    assert any(h["event"] == "pull" for h in hooks)


def test_set_webhook_raises_if_vault_missing():
    with patch("envault.webhook.vault_exists", return_value=False):
        with pytest.raises(WebhookError, match="not found"):
            set_webhook("ghost", PASS, "push", "https://example.com")


def test_remove_webhook_removes_entry(mock_webhook_deps):
    set_webhook(VAULT, PASS, "push", "https://example.com/hook")
    result = remove_webhook(VAULT, PASS, "push")
    assert result["status"] == "removed"
    hooks = list_webhooks(VAULT, PASS)
    assert not any(h["event"] == "push" for h in hooks)


def test_remove_webhook_raises_if_not_registered(mock_webhook_deps):
    with pytest.raises(WebhookError, match="No webhook"):
        remove_webhook(VAULT, PASS, "nonexistent")


def test_list_webhooks_empty_by_default(mock_webhook_deps):
    hooks = list_webhooks(VAULT, PASS)
    assert hooks == []


def test_fire_webhook_no_registration(mock_webhook_deps):
    result = fire_webhook(VAULT, PASS, "push")
    assert result["fired"] is False


def test_fire_webhook_calls_url(mock_webhook_deps):
    set_webhook(VAULT, PASS, "push", "https://example.com/hook")
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = fire_webhook(VAULT, PASS, "push", {"key": "DB_HOST"})
    assert result["fired"] is True
    assert result["http_status"] == 200


def test_cmd_set_webhook_ok(mock_webhook_deps):
    result = cmd_set_webhook(VAULT, PASS, "push", "https://example.com")
    assert result["ok"] is True


def test_cmd_remove_webhook_ok(mock_webhook_deps):
    set_webhook(VAULT, PASS, "push", "https://example.com")
    result = cmd_remove_webhook(VAULT, PASS, "push")
    assert result["ok"] is True


def test_cmd_list_webhooks_count(mock_webhook_deps):
    set_webhook(VAULT, PASS, "push", "https://a.com")
    set_webhook(VAULT, PASS, "pull", "https://b.com")
    result = cmd_list_webhooks(VAULT, PASS)
    assert result["ok"] is True
    assert result["count"] == 2


def test_format_webhook_list_empty():
    assert format_webhook_list([]) == "No webhooks registered."


def test_format_webhook_list_shows_entries():
    hooks = [{"event": "push", "url": "https://example.com"}]
    output = format_webhook_list(hooks)
    assert "push" in output
    assert "https://example.com" in output
