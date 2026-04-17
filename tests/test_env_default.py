import pytest
from unittest.mock import patch
from envault.env_default import set_defaults, get_defaults_preview, DefaultError, format_defaults_result

BASE = {"HOST": "localhost", "PORT": "5432"}


@pytest.fixture
def mock_deps():
    with patch("envault.env_default.vault_exists") as _exists, \
         patch("envault.env_default.get_env_vars") as _get, \
         patch("envault.env_default.push_env") as _push:
        _exists.return_value = True
        _get.return_value = dict(BASE)
        yield _exists, _get, _push


def test_set_defaults_applies_missing_keys(mock_deps):
    _, _, _push = mock_deps
    result = set_defaults("myapp", "pass", {"DEBUG": "false", "HOST": "other"})
    assert result["applied"] == {"DEBUG": "false"}
    assert "HOST" in result["skipped"]


def test_set_defaults_overwrite_replaces_existing(mock_deps):
    _, _, _push = mock_deps
    result = set_defaults("myapp", "pass", {"HOST": "newhost"}, overwrite=True)
    assert result["applied"] == {"HOST": "newhost"}
    assert result["skipped"] == {}


def test_set_defaults_calls_push_when_applied(mock_deps):
    _, _, _push = mock_deps
    set_defaults("myapp", "pass", {"NEW_KEY": "val"})
    _push.assert_called_once()


def test_set_defaults_no_push_when_nothing_applied(mock_deps):
    _, _, _push = mock_deps
    set_defaults("myapp", "pass", {"HOST": "x", "PORT": "y"})
    _push.assert_not_called()


def test_set_defaults_raises_if_vault_missing(mock_deps):
    _exists, _, _ = mock_deps
    _exists.return_value = False
    with pytest.raises(DefaultError, match="not found"):
        set_defaults("ghost", "pass", {"X": "1"})


def test_preview_shows_would_apply_and_skip(mock_deps):
    result = get_defaults_preview("myapp", "pass", {"HOST": "x", "NEW": "y"})
    assert "HOST" in result["would_skip"]
    assert "NEW" in result["would_apply"]


def test_format_defaults_result_includes_applied():
    result = {
        "vault": "myapp",
        "applied": {"DEBUG": "false"},
        "skipped": {"HOST": "localhost"},
        "total_applied": 1,
        "total_skipped": 1,
    }
    out = format_defaults_result(result)
    assert "DEBUG=false" in out
    assert "HOST" in out


def test_format_defaults_result_empty():
    result = {"vault": "myapp", "applied": {}, "skipped": {}, "total_applied": 0, "total_skipped": 0}
    out = format_defaults_result(result)
    assert "No defaults" in out
