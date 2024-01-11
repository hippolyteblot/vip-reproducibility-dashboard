"""
Test the app.py file
"""
from tests.conftest import client


def test_should_status_code_ok(client):
    """Test if the status code is 200 for all pages"""
    response = client.get('/')
    assert response.status_code == 200
    response = client.get('/abcd')
    assert response.status_code == 200
    response = client.get('/reproducibility')
    assert response.status_code == 200
    response = client.get('/login')
    assert response.status_code == 200
    response = client.get('/add-experiment')
    assert response.status_code == 200
    response = client.get('/repro-experiment')
    assert response.status_code == 200
    response = client.get('/repro-execution')
    assert response.status_code == 200
