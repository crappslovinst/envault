"""Webhook notifications for vault events."""

import json
import urllib.request
import urllib.error
from typing import Optional

from envault.storage import load_vault, save_vault, vault_exists


class WebhookError(Exception):
    pass


def _get_webhooks(vault: dict) -> dict:
    return vault.get("__meta__", {}).get("webhooks", {})


def set_webhook(vault_name: str, password: str, event: str, url: str) -> dict:
    """Register a webhook URL for a specific event on a vault."""
    if not vault_exists(vault_name):
        raise WebhookError(f"Vault '{vault_name}' not found")
    vault = load_vault(vault_name, password)
    meta = vault.setdefault("__meta__", {})
    webhooks = meta.setdefault("webhooks", {})
    webhooks[event] = url
    save_vault(vault_name, password, vault)
    return {"vault": vault_name, "event": event, "url": url, "status": "registered"}


def remove_webhook(vault_name: str, password: str, event: str) -> dict:
    """Remove a registered webhook for a specific event."""
    if not vault_exists(vault_name):
        raise WebhookError(f"Vault '{vault_name}' not found")
    vault = load_vault(vault_name, password)
    webhooks = _get_webhooks(vault)
    if event not in webhooks:
        raise WebhookError(f"No webhook registered for event '{event}'")
    del vault["__meta__"]["webhooks"][event]
    save_vault(vault_name, password, vault)
    return {"vault": vault_name, "event": event, "status": "removed"}


def list_webhooks(vault_name: str, password: str) -> list:
    """List all registered webhooks for a vault."""
    if not vault_exists(vault_name):
        raise WebhookError(f"Vault '{vault_name}' not found")
    vault = load_vault(vault_name, password)
    webhooks = _get_webhooks(vault)
    return [{"event": k, "url": v} for k, v in webhooks.items()]


def fire_webhook(
    vault_name: str, password: str, event: str, payload: Optional[dict] = None
) -> dict:
    """Fire the webhook for a given event if one is registered."""
    if not vault_exists(vault_name):
        raise WebhookError(f"Vault '{vault_name}' not found")
    vault = load_vault(vault_name, password)
    webhooks = _get_webhooks(vault)
    if event not in webhooks:
        return {"vault": vault_name, "event": event, "fired": False, "reason": "no webhook registered"}
    url = webhooks[event]
    body = json.dumps({"vault": vault_name, "event": event, **(payload or {})}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
    except urllib.error.URLError as exc:
        raise WebhookError(f"Webhook delivery failed: {exc}") from exc
    return {"vault": vault_name, "event": event, "fired": True, "url": url, "http_status": status}
