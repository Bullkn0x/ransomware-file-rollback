import os
import pytest
from rollback.create import create_sample_files, update_sample_files
from rollback.utils.helpers import get_cli_args
import argparse
from unittest import mock
@pytest.fixture
def created_files(tmpdir):
    # Create the sample files in the temporary directory
    create_sample_files(num_files=3, directory=str(tmpdir))

    yield tmpdir

    # Delete the files after the tests have run
    for file_name in os.listdir(str(tmpdir)):
        if file_name.startswith("sample_file") and file_name.endswith(".txt"):
            os.remove(os.path.join(str(tmpdir), file_name))

def test_create_files(created_files):
    # Assert that the sample files were created
    assert len(os.listdir(str(created_files))) == 3

def test_update_files(created_files):
    # Update the sample files
    update_sample_files(directory=str(created_files))

    # Assert that the files were updated
    for file_name in os.listdir(str(created_files)):
        if file_name.startswith("sample_file") and file_name.endswith(".txt"):
            with open(os.path.join(str(created_files), file_name), "r") as f:
                contents = f.read()
                assert "File updated on" in contents


def test_get_cli_args_create():
    with mock.patch('sys.argv', ['test.py', '-c', '10']):
        args = get_cli_args()
        assert args.create == 10
        assert args.update is False
        assert args.directory == 'test_files/'
        assert args.wizard is None

def test_get_cli_args_update():
    with mock.patch('sys.argv', ['test.py', '-u']):
        args = get_cli_args()
        assert args.create is None
        assert args.update is True
        assert args.directory == 'test_files/'
        assert args.wizard is None

def test_get_cli_args_directory():
    with mock.patch('sys.argv', ['test.py', '-c', '5', '-dir', '/tmp']):
        args = get_cli_args()
        assert args.create == 5
        assert args.update is False
        assert args.directory == '/tmp'
        assert args.wizard is None

def test_get_cli_args_encrypt():
    with mock.patch('sys.argv', ['test.py', '-c', '5', '-enc']):
        args = get_cli_args()
        assert args.create == 5
        assert args.update is False
        assert args.encrypt is True
        assert args.decrypt is False
        assert args.directory == 'test_files/'
        assert args.wizard is None

def test_get_cli_args_decrypt():
    with mock.patch('sys.argv', ['test.py', '-dec']):
        args = get_cli_args()
        assert args.create is None
        assert args.update is False
        assert args.encrypt is False
        assert args.decrypt is True
        assert args.directory == 'test_files/'
        assert args.wizard is None

def test_get_cli_args_all():
    with mock.patch('sys.argv', ['test.py', '-c', '10', '-u', '-enc', '-dec', '-dir', '/tmp', '-w', 'my_wizard']):
        args = get_cli_args()
        assert args.create == 10
        assert args.update is True
        assert args.encrypt is True
        assert args.decrypt is True
        assert args.directory == '/tmp'
        assert args.wizard == 'my_wizard'