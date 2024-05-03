import pytest


@pytest.fixture
def mock_db_and_gvc(mocker):
    mock_db = mocker.patch("utils.settings.get_DB")
    mock_gvc = mocker.patch("utils.settings.get_girder_client")
    return mock_db, mock_gvc