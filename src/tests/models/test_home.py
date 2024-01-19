import os
import pytest

from models.home import flatten_folder, build_wf_json_from_db, decode_base64
from unittest.mock import MagicMock
from utils.settings import GVC


@pytest.fixture
def mock_girder_client():
    mock_girder_client = MagicMock(spec=GVC)
    return mock_girder_client


def test_flatten_folder(tmp_path):
    # Create the structure
    directory = tmp_path / "folder"
    directory.mkdir()
    subdir = directory / "sub"
    subdir.mkdir()
    subdir2 = subdir / "subsub"
    subdir2.mkdir()
    f = subdir / "hello.txt"
    f.write_text("content")
    f2 = subdir2 / "hello2.txt"
    f2.write_text("content2")

    # Flatten the folder
    flatten_folder(tmp_path / "folder")

    # Check content
    assert sorted(os.listdir(directory)) == ["hello.txt", "hello2.txt"]

    # Check content of hello.txt
    assert (directory / "hello.txt").read_text() == "content"

    # Check content of hello2.txt
    assert (directory / "hello2.txt").read_text() == "content2"


def test_build_wf_json_from_db():
    data = [
        {
            "workflow_id": 1,
            "workflow_name": "workflow1",
            "application_name": "app1",
            "experiment_name": "exp1",
            "application_version": "1.0",
            "application_id": 1,
            "version_id": 1
        },
        {
            "workflow_id": 2,
            "workflow_name": "workflow2",
            "application_name": "app2",
            "experiment_name": "exp2",
            "application_version": "2.0",
            "application_id": 2,
            "version_id": 2
        }
    ]
    expected = [
        {
            "id": 1,
            "name": "workflow1",
            "application_name": "app1",
            "experiment_name": "exp1",
            "application_version": "1.0",
            "application_id": 1,
            "version_id": 1
        },
        {
            "id": 2,
            "name": "workflow2",
            "application_name": "app2",
            "experiment_name": "exp2",
            "application_version": "2.0",
            "application_id": 2,
            "version_id": 2
        }
    ]
    assert build_wf_json_from_db(data) == expected


def test_decode_base64():
    assert decode_base64("aGVsbG8=") == b"hello"
    assert decode_base64("aGVsbG8gZnJvbSB0ZXN0") == b"hello from test"
    assert not decode_base64("aGVsbG8gZnJvbSB0ZXN0") == b"hello from test2"
