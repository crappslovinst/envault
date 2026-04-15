"""CLI operations for webhook management."""

from envault.webhook import set_webhook, remove_webhook, list_webhooks, WebhookError


def cmd_set_webhook(vault_name: str, password: str, event: str, url: str) -> dict:
    """Register or update a webhook URL for a vault event."""
    try:
        result = set_webhook(vault_name, password, event, url)
        return {"ok": True, "message": f"Webhook set for '{event}' on vault '{vault_name}'", **result}
    except WebhookError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_remove_webhook(vault_name: str, password: str, event: str) -> dict:
    """Remove a registered webhook from a vault."""
    try:
        result = remove_webhook(vault_name, password, event)
        return {"ok": True, "message": f"Webhook for '{event}' removed", **result}
    except WebhookError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_list_webhooks(vault_name: str, password: str) -> dict:
    """List all webhooks registered for a vault."""
    try:
        hooks = list_webhooks(vault_name, password)
        return {"ok": True, "vault": vault_name, "webhooks": hooks, "count": len(hooks)}
    except WebhookError as exc:
        return {"ok": False, "error": str(exc)}


def format_webhook_list(hooks: list) -> str:
    """Format a list of webhook entries for display."""
    if not hooks:
        return "No webhooks registered."
    lines = []
    for h in hooks:
        lines.append(f"  [{h['event']}] -> {h['url']}")
    return "\n".join(lines)
