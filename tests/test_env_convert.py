import pytest
from unittest.mock import patch, MagicMock
from envault.env_convert import convert_keys, format_convert_result, ConvertError, _to_snake, _to_camel, _to_screaming_snake


@pytest.fixture
def mock_convert_deps():
    with patch('envault.env_convert.vault_exists') as _exists, \
         patch('envault.env_convert.get_env_vars') as _get, \
         patch('envault.env_convert.push_env') as _push:
        _exists.return_value = True
        yield _exists, _get, _push


def test_to_snake_from_camel():
    assert _to_snake('myApiKey') == 'my_api_key'


def test_to_snake_already_snake():
    assert _to_snake('my_key') == 'my_key'


def test_to_screaming_snake():
    assert _to_screaming_snake('myApiKey') == 'MY_API_KEY'


def test_to_camel_from_snake():
    assert _to_camel('my_api_key') == 'myApiKey'


def test_convert_raises_on_unknown_convention(mock_convert_deps):
    with pytest.raises(ConvertError, match='Unknown convention'):
        convert_keys('myvault', 'pass', 'pascal')


def test_convert_raises_if_vault_missing(mock_convert_deps):
    _exists, _, _ = mock_convert_deps
    _exists.return_value = False
    with pytest.raises(ConvertError, match='not found'):
        convert_keys('myvault', 'pass', 'snake')


def test_convert_screaming_snake_renames(mock_convert_deps):
    _, _get, _push = mock_convert_deps
    _get.return_value = {'myApiKey': 'val1', 'dbHost': 'localhost'}
    result = convert_keys('v', 'p', 'screaming_snake')
    assert result['convention'] == 'screaming_snake'
    assert 'myApiKey' in result['renamed']
    assert result['renamed']['myApiKey'] == 'MY_API_KEY'
    _push.assert_called_once()


def test_convert_dry_run_skips_push(mock_convert_deps):
    _, _get, _push = mock_convert_deps
    _get.return_value = {'myKey': 'v'}
    result = convert_keys('v', 'p', 'snake', dry_run=True)
    assert result['dry_run'] is True
    _push.assert_not_called()


def test_convert_no_push_when_no_renames(mock_convert_deps):
    _, _get, _push = mock_convert_deps
    _get.return_value = {'MY_KEY': 'v', 'DB_HOST': 'h'}
    convert_keys('v', 'p', 'screaming_snake')
    _push.assert_not_called()


def test_format_convert_result_contains_keys():
    result = {
        'vault': 'dev', 'convention': 'snake',
        'renamed': {'myKey': 'my_key'}, 'collisions': 0,
        'total': 3, 'dry_run': False,
    }
    out = format_convert_result(result)
    assert 'myKey' in out
    assert 'my_key' in out
    assert 'snake' in out


def test_format_convert_result_dry_run_note():
    result = {
        'vault': 'dev', 'convention': 'camel',
        'renamed': {}, 'collisions': 0,
        'total': 2, 'dry_run': True,
    }
    out = format_convert_result(result)
    assert 'dry run' in out
