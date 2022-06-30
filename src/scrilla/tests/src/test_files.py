import pytest
from unittest.mock import patch, ANY

from scrilla import files, settings

@patch('scrilla.files.json.load')
def test_get_memory_json(load_function):
    test_memory = { 'test': 'this is'}
    load_function.return_value = test_memory

    memory_json = files.get_memory_json()

    assert memory_json == test_memory

@patch('scrilla.files.os.path.isfile')
def test_get_memory_json_when_doesnt_exist(existence_function):
    existence_function.return_value = False

    memory_json = files.get_memory_json()

    assert not memory_json['static']
    assert all(not falsehood for falsehood in memory_json['cache']['sqlite'].values())
    assert all(not falsehood for falsehood in memory_json['cache']['dynamodb'].values())

@patch('scrilla.files.json.dump')
def test_save_memory_json(save_function):
    test_memory = {'a trial': 'by fire'}

    files.save_memory_json(test_memory)

    save_function.assert_called()
    save_function.assert_called_with(test_memory, ANY)
