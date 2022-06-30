import pytest
from unittest.mock import patch

from scrilla import files

@patch('scrilla.files.json.load')
def test_get_memory_json(load_function):
    load_function.return_value = { 'test': 'this is'}
    memory_json = files.get_memory_json()
    assert memory_json == {'test': 'this is'}

@patch('scrilla.files.os.path.isfile')
def test_get_memory_json_when_doesnt_exist(existence_function):
    existence_function.return_value = False
    memory_json = files.get_memory_json()
    assert not memory_json['static']
    assert all(not falsehood for falsehood in memory_json['cache']['sqlite'].values())
    assert all(not falsehood for falsehood in memory_json['cache']['dynamodb'].values())
