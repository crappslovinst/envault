import pytest
from unittest.mock import patch, MagicMock
from envault.env_promote import promote_vault, PromoteError


SRC_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
DST_VARS = {"DB_HOST": "prod-db", "APP_ENV": "production"}


@pytest.fixture
def mock_promote_deps():
    with patch("envault.env_promote.vault_exists") as mock_exists, \
         patch("envault.env_promote.get_env_vars") as mock_get, \
         patch("envault.env_promote.push_env") as mock_push, \
         patch("envault.env_promote.record_event") as mock_audit:
        yield mock_exists, mock_get, mock_push, mock_audit


def test_promote_raises_if_src_missing(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.return_value = False
    with pytest.raises(PromoteError, match="Source vault"):
        promote_vault("staging", "prod", "pass1", "pass2")


def test_promote_all_keys(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else DST_VARS

    result = promote_vault("staging", "prod", "pass1", "pass2")

    assert set(result["promoted"]) == set(SRC_VARS.keys())
    assert result["skipped"] == []
    assert result["missing"] == []
    mock_push.assert_called_once()


def test_promote_specific_keys(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else {}

    result = promote_vault("staging", "prod", "pass1", "pass2", keys=["DB_HOST", "DB_PORT"])

    assert result["promoted"] == ["DB_HOST", "DB_PORT"]
    assert result["missing"] == []


def test_promote_missing_keys_reported(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else {}

    result = promote_vault("staging", "prod", "pass1", "pass2", keys=["DB_HOST", "NONEXISTENT"])

    assert "NONEXISTENT" in result["missing"]
    assert "DB_HOST" in result["promoted"]


def test_promote_no_overwrite_skips_existing(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else DST_VARS

    result = promote_vault("staging", "prod", "pass1", "pass2", overwrite=False)

    assert "DB_HOST" in result["skipped"]
    assert "DB_PORT" in result["promoted"]


def test_promote_creates_dst_if_missing(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: v == "staging"
    mock_get.return_value = SRC_VARS

    result = promote_vault("staging", "new-prod", "pass1", "pass2")

    assert set(result["promoted"]) == set(SRC_VARS.keys())
    mock_push.assert_called_once()


def test_promote_records_audit_event(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else {}

    promote_vault("staging", "prod", "pass1", "pass2")

    mock_audit.assert_called_once()
    call_kwargs = mock_audit.call_args
    assert call_kwargs.kwargs["action"] == "promote"
    assert call_kwargs.kwargs["vault"] == "prod"


def test_promote_returns_vault_names(mock_promote_deps):
    mock_exists, mock_get, mock_push, mock_audit = mock_promote_deps
    mock_exists.side_effect = lambda v: True
    mock_get.side_effect = lambda vault, pw: SRC_VARS if vault == "staging" else {}

    result = promote_vault("staging", "prod", "pass1", "pass2")

    assert result["src_vault"] == "staging"
    assert result["dst_vault"] == "prod"
