import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_recommendations_api(client):
    payload = {
        "city": "Lima",
        "maxt": "30",
        "mint": "15",
        "precipitation": "20",
        "description": "Nublado"
    }
    response = client.post('/api/recommendations', json=payload)
    assert response.status_code == 200
