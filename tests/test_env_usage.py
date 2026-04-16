import pytest
from unittest.mock import patch, MagicMock
from envault.env_usage import record_access, get_usage, clear_usage, top_keys, UsageError

VAULT = "myvault"
PASS = "secret"


@pytest.fixture
def mock_deps():
    vault_data = {"KEY1": "val1", "KEY2": "val2"}
    exists = MagicMock(return_value=True)
    load = MagicMock(return_value=vault_data)
    save = MagicMock()
    with patch("envault.env_usage.vault_exists", exists), \
         patch("envault.env_usage.load_vault", load), \
         patch("envault.env_usage.save_vault", save):
        yield {"exists": exists, "load": load, "save": save, "data": vault_data}


def test_record_access_returns_entry(mock_deps):
    result = record_access(VAULT, "KEY1", PASS)
    assert result["count"] == 1
    assert result["last_accessed"] is not None


def test_record_access_increments_count(mock_deps):
    mock_deps["data"]["__usage__"] = {
        "KEY1": {"count": 3, "first_accessed": "2024-01-01T00:00:00+00:00", "last_accessed": "2024-01-02T00:00:00+00:00"}
    }
    result = record_access(VAULT, "KEY1", PASS)
    assert result["count"] == 4


def test_record_access_raises_if_vault_missing():
    with patch("envault.env_usage.vault_exists", return_value=False):
        with pytest.raises(UsageError, match="not found"):
            record_access(VAULT, "KEY1", PASS)


def test_get_usage_all_keys(mock_deps):
    mock_deps["data"]["__usage__"] = {
        "KEY1": {"count": 2, "first_accessed": "x", "last_accessed": "y"},
        "KEY2": {"count": 5, "first_accessed": "x", "last_accessed": "y"},
    }
    result = get_usage(VAULT, PASS)
    assert "KEY1" in result
    assert "KEY2" in result


def test_get_usage_single_key(mock_deps):
    mock_deps["data"]["__usage__"] = {
        "KEY1": {"count": 7, "first_accessed": "x", "last_accessed": "y"},
    }
    result = get_usage(VAULT, PASS, key="KEY1")
    assert result["KEY1"]["count"] == 7


def test_get_usage_missing_key_returns_zero(mock_deps):
    mock_deps["data"]["__usage__"] = {}
    result = get_usage(VAULT, PASS, key="MISSING")
    assert result["MISSING"]["count"] == 0


def test_clear_usage_resets_stats(mock_deps):
    mock_deps["data"]["__usage__"] = {"KEY1": {"count": 10}}
    result = clear_usage(VAULT, PASS)
    assert result["status"] == "cleared"
    saved = mock_deps["save"].call_args[0][1]
    assert saved["__usage__"] == {}


def test_top_keys_returns_ranked_list(mock_deps):
    mock_deps["data"]["__usage__"] = {
        "A": {"count": 1, "first_accessed": "x", "last_accessed": "y"},
        "B": {"count": 9, "first_accessed": "x", "last_accessed": "y"},
        "C": {"count": 4, "first_accessed": "x", "last_accessed": "y"},
    }
    result = top_keys(VAULT, PASS, n=2)
    assert len(result) == 2
    assert result[0]["key"] == "B"
    assert result[1]["key"] == "C"


def test_top_keys_raises_if_vault_missing():
    with patch("envault.env_usage.vault_exists", return_value=False):
        with pytest.raises(UsageError):
            top_keys(VAULT, PASS)
