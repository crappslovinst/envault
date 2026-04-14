"""Tests for envault/history.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.history import (
    HistoryError,
    record_snapshot,
    get_history,
    rollback,
    _HISTORY_KEY,
    MAX_HISTORY,
)


@pytest.fixture
def mock_storage(tmp_path):
    """Patch storage functions and provide a simple in-memory vault."""
    vault_store: dict = {}

    def _exists(name):
        return name in vault_store

    def _load(name, password):
        return dict(vault_store[name])

    def _save(name, data, password):
        vault_store[name] = dict(data)

    with (
        patch("envault.history.vault_exists", side_effect=_exists),
        patch("envault.history.load_vault", side_effect=_load),
        patch("envault.history.save_vault", side_effect=_save),
    ):
        yield vault_store


def test_record_snapshot_raises_if_vault_missing(mock_storage):
    with pytest.raises(HistoryError, match="not found"):
        record_snapshot("ghost", "pw", "push")


def test_record_snapshot_appends_entry(mock_storage):
    mock_storage["myapp"] = {"KEY": "value"}
    entry = record_snapshot("myapp", "pw", "push")
    assert entry["action"] == "push"
    assert entry["snapshot"] == {"KEY": "value"}
    assert "timestamp" in entry


def test_record_snapshot_persists_to_vault(mock_storage):
    mock_storage["myapp"] = {"A": "1"}
    record_snapshot("myapp", "pw", "push")
    assert _HISTORY_KEY in mock_storage["myapp"]
    assert len(mock_storage["myapp"][_HISTORY_KEY]) == 1


def test_record_snapshot_trims_to_max_history(mock_storage):
    mock_storage["myapp"] = {"X": "y"}
    for i in range(MAX_HISTORY + 5):
        record_snapshot("myapp", "pw", "push")
    history = mock_storage["myapp"][_HISTORY_KEY]
    assert len(history) == MAX_HISTORY


def test_get_history_returns_most_recent_first(mock_storage):
    mock_storage["myapp"] = {"K": "1"}
    record_snapshot("myapp", "pw", "push")
    mock_storage["myapp"]["K"] = "2"
    record_snapshot("myapp", "pw", "pull")
    history = get_history("myapp", "pw")
    assert history[0]["action"] == "pull"
    assert history[1]["action"] == "push"


def test_get_history_raises_if_vault_missing(mock_storage):
    with pytest.raises(HistoryError):
        get_history("nope", "pw")


def test_rollback_restores_env_vars(mock_storage):
    mock_storage["myapp"] = {"DB": "old"}
    record_snapshot("myapp", "pw", "push")
    mock_storage["myapp"]["DB"] = "new"
    record_snapshot("myapp", "pw", "push")

    result = rollback("myapp", "pw", index=1)  # second most recent = original
    assert result["keys_restored"] == 1
    assert mock_storage["myapp"]["DB"] == "old"


def test_rollback_raises_on_empty_history(mock_storage):
    mock_storage["myapp"] = {"K": "v"}
    with pytest.raises(HistoryError, match="No history"):
        rollback("myapp", "pw")


def test_rollback_raises_on_bad_index(mock_storage):
    mock_storage["myapp"] = {"K": "v"}
    record_snapshot("myapp", "pw", "push")
    with pytest.raises(HistoryError, match="out of range"):
        rollback("myapp", "pw", index=99)


def test_rollback_preserves_meta_keys(mock_storage):
    mock_storage["myapp"] = {"K": "v", "__tags__": ["prod"]}
    record_snapshot("myapp", "pw", "push")
    rollback("myapp", "pw", index=0)
    assert "__tags__" in mock_storage["myapp"]
