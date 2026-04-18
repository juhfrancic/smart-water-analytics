# tests/test_api.py

import pytest
from app.backend.app import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


# -------------------------
# TESTE: rota home (/)
# -------------------------
def test_home(client):
    response = client.get("/")
    data = response.get_json()

    assert response.status_code == 200
    assert data["projeto"] == "SmartWater API"
    assert data["status"] == "online"


# -------------------------
# TESTE: GET alertas
# -------------------------
def test_get_alertas(client):
    response = client.get("/api/alertas")
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert "local" in data[0]


# -------------------------
# TESTE: POST leitura OK
# -------------------------
def test_post_leitura_ok(client):
    payload = {
        "id_sensor": 1,
        "valor": 55
    }

    response = client.post("/api/sensor/leitura", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["status"] == "sucesso"


# -------------------------
# TESTE: POST sem dados (erro)
# -------------------------
def test_post_leitura_erro(client):
    response = client.post(
        "/api/sensor/leitura",
        json={}   
    )
    data = response.get_json()

    assert response.status_code == 400
    assert "erro" in data