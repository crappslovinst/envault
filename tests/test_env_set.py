import pytest
from unittest.mock import patch, MagicMock
from envault.env_set import SetError, set_key, delete_key, set_many


@pytest.fixture
def mock_set_deps():
    env_data = {"EXISTING": "val"}

    def _exists(v):
        return v == "myvault"

    def _get(v, p):
        return dict(env_data)

    pushed = {}

    def _push(v, p, data):
        pushed["data"] = data

    with patch("envault.env_set.vault_exists", side_effect=_exists), \
         patch("envault.env_set.get_env_vars", side_effect=_get), \
         patch("envault.env_set.push_env", side_effect=_push):
        yield pushed


def test_set_key_creates_new(mock_set_deps):
    result = set_key("myvault", "pass", "NEW_KEY", "newval")
    assert result["status"] == "created"
    assert result["key"] == "NEW_KEY"
    assert mock_set_deps["data"]["NEW_KEY"] == "newval"


def test_set_key_updates_existing(mock_set_deps):
    result = set_key("myvault", "pass", "EXISTING", "changed")
    assert result["status"] == "updated"
    assert mock_set_deps["data"]["EXISTING"] == "changed"


def test_set_key_skips_if_no_overwrite(mock_set_deps):
    result = set_key("myvault", "pass", "EXISTING", "nope", overwrite=False)
    assert result["status"] == "skipped"


def test_set_key_raises_if_vault_missing():
    with patch("envault.env_set.vault_exists", return_value=False):
        with pytest.raises(SetError, match="not found"):
            set_key("ghost", "pass", "K", "V")


def test_delete_key_removes_existing(mock_set_deps):
    result = delete_key("myvault", "pass", "EXISTING")
    assert result["status"] == "deleted"
    assert "EXISTING" not in mock_set_deps["data"]


def test_delete_key_raises_if_key_missing(mock_set_deps):
    with pytest.raises(SetError, match="not found"):
        delete_key("myvault", "pass", "GHOST_KEY")


def test_delete_key_raises_if_vault_missing():
    with patch("envault.env_set.vault_exists", return_value=False):
        with pytest.raises(SetError):
            delete_key("ghost", "pass", "K")


def test_set_many_sets_all(mock_set_deps):
    result = set_many("myvault", "pass", {"A": "1", "B": "2"})
    assert result["count"] == 2
    assert result["results"]["A"] == "created"
    assert result["results"]["B"] == "created"


def test_set_many_respects_overwrite_false(mock_set_deps):
    result = set_many("myvault", "pass", {"EXISTING": "x", "NEW": "y"}, overwrite=False)
    assert result["results"]["EXISTING"] == "skipped"
    assert result["results"]["NEW"] == "created"


def test_set_many_raises_if_vault_missing():
    with patch("envault.env_set.vault_exists", return_value=False):
        with pytest.raises(SetError):
            set_many("ghost", "pass", {"K": "V"})
