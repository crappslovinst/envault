import pytest
from unittest.mock import patch, MagicMock
from envault.env_annotate import (
    set_annotation, remove_annotation, get_annotations, format_annotations, AnnotateError
)

VAULT = "myvault"
PASS = "secret"


@pytest.fixture
def mock_deps():
    base_data = {"KEY": "val"}
    saved = {}

    def _exists(name):
        return name == VAULT

    def _load(name, pw):
        return dict(saved.get(name, base_data))

    def _save(name, pw, data):
        saved[name] = dict(data)

    with patch("envault.env_annotate.vault_exists", side_effect=_exists), \
         patch("envault.env_annotate.load_vault", side_effect=_load), \
         patch("envault.env_annotate.save_vault", side_effect=_save):
        yield saved


def test_set_annotation_returns_summary(mock_deps):
    result = set_annotation(VAULT, PASS, "KEY", "This is the API key")
    assert result["status"] == "set"
    assert result["key"] == "KEY"
    assert result["annotation"] == "This is the API key"


def test_set_annotation_persists(mock_deps):
    set_annotation(VAULT, PASS, "KEY", "some note")
    annotations = get_annotations(VAULT, PASS)
    assert annotations.get("KEY") == "some note"


def test_set_annotation_raises_if_vault_missing():
    with patch("envault.env_annotate.vault_exists", return_value=False):
        with pytest.raises(AnnotateError):
            set_annotation("ghost", PASS, "KEY", "note")


def test_remove_annotation_returns_summary(mock_deps):
    set_annotation(VAULT, PASS, "KEY", "note")
    result = remove_annotation(VAULT, PASS, "KEY")
    assert result["status"] == "removed"


def test_remove_annotation_raises_if_key_missing(mock_deps):
    with pytest.raises(AnnotateError, match="No annotation"):
        remove_annotation(VAULT, PASS, "NONEXISTENT")


def test_get_annotations_single_key(mock_deps):
    set_annotation(VAULT, PASS, "KEY", "hello")
    result = get_annotations(VAULT, PASS, key="KEY")
    assert result == {"KEY": "hello"}


def test_get_annotations_all(mock_deps):
    set_annotation(VAULT, PASS, "A", "note a")
    set_annotation(VAULT, PASS, "B", "note b")
    result = get_annotations(VAULT, PASS)
    assert "A" in result and "B" in result


def test_format_annotations_empty():
    assert format_annotations({}) == "No annotations."


def test_format_annotations_shows_keys():
    out = format_annotations({"FOO": "bar", "BAZ": "qux"})
    assert "FOO" in out
    assert "bar" in out
