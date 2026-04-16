"""Tests for envault/env_status.py"""

import pytest
from unittest.mock import patch
from envault.env_status import StatusError, get_status, format_status


@pytest.fixture
def mock_status_deps():
    with patch("envault.env_status.vault_exists") as mock_exists, \
         patch("envault.env_status.get_ttl") as mock_ttl, \
         patch("envault.env_status.is_expired") as mock_expired, \
         patch("envault.env_status.is_locked") as mock_locked, \
         patch("envault.env_status.get_tags") as mock_tags, \
         patch("envault.env_status.get_events") as mock_events:
        mock_exists.return_value = True
        mock_ttl.return_value = None
        mock_expired.return_value = False
        mock_locked.return_value = False
        mock_tags.return_value = []
        mock_events.return_value = []
        yield {
            "exists": mock_exists,
            "ttl": mock_ttl,
            "expired": mock_expired,
            "locked": mock_locked,
            "tags": mock_tags,
            "events": mock_events,
        }


def test_get_status_raises_if_vault_missing(mock_status_deps):
    mock_status_deps["exists"].return_value = False
    with pytest.raises(StatusError, match="does not exist"):
        get_status("ghost", "pw")


def test_get_status_returns_dict(mock_status_deps):
    result = get_status("myapp", "pw")
    assert result["vault"] == "myapp"
    assert result["locked"] is False
    assert result["expired"] is False
    assert result["tags"] == []
    assert result["event_count"] == 0
    assert result["last_event"] is None


def test_get_status_reflects_locked(mock_status_deps):
    mock_status_deps["locked"].return_value = True
    result = get_status("myapp", "pw")
    assert result["locked"] is True


def test_get_status_reflects_expired(mock_status_deps):
    mock_status_deps["ttl"].return_value = {"expires_at": "2020-01-01T00:00:00"}
    mock_status_deps["expired"].return_value = True
    result = get_status("myapp", "pw")
    assert result["expired"] is True
    assert result["ttl"] is not None


def test_get_status_last_event(mock_status_deps):
    events = [
        {"action": "push", "timestamp": "2024-01-01T10:00:00"},
        {"action": "pull", "timestamp": "2024-01-02T10:00:00"},
    ]
    mock_status_deps["events"].return_value = events
    result = get_status("myapp", "pw")
    assert result["event_count"] == 2
    assert result["last_event"]["action"] == "pull"


def test_get_status_includes_tags(mock_status_deps):
    mock_status_deps["tags"].return_value = ["production", "critical"]
    result = get_status("myapp", "pw")
    assert "production" in result["tags"]


def test_format_status_contains_vault_name(mock_status_deps):
    result = get_status("myapp", "pw")
    text = format_status(result)
    assert "myapp" in text


def test_format_status_shows_no_ttl(mock_status_deps):
    result = get_status("myapp", "pw")
    text = format_status(result)
    assert "none" in text


def test_format_status_shows_tags(mock_status_deps):
    mock_status_deps["tags"].return_value = ["staging"]
    result = get_status("myapp", "pw")
    text = format_status(result)
    assert "staging" in text


def test_format_status_shows_last_event(mock_status_deps):
    mock_status_deps["events"].return_value = [
        {"action": "push", "timestamp": "2024-06-01T12:00:00"}
    ]
    result = get_status("myapp", "pw")
    text = format_status(result)
    assert "push" in text
