import pytest

from app.main import app


def test_create_service_account(client):
    response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service Account",
            "phone": "+5511987654322",
            "description": "A test service account",
        },
    )
    assert response.status_code == 201
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert res["message"] == "Service account created successfully"
    assert data["name"] == "Test Service Account"
    assert data["phone"] == "+5511987654322"
    assert data["description"] == "A test service account"
    assert "id" in data


def test_create_service_account_with_invalid_phone(client):
    response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service Account",
            "phone": "invalid-phone",
            "description": "A test service account",
        },
    )
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res


def test_get_service_account(client):
    create_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service",
            "phone": "+5511987654322",
            "description": "A test service",
        },
    )
    service_account_id = create_response.json()["data"]["id"]

    response = client.get(f"/service-accounts/{service_account_id}")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["name"] == "Test Service"
    assert data["phone"] == "+5511987654322"
    assert data["description"] == "A test service"
    assert "appointments" in data


def test_get_all_service_accounts(client):
    client.post(
        "/service-accounts/",
        json={
            "name": "Service Account 1",
            "phone": "+5511987654322",
            "description": "First test service",
        },
    )

    client.post(
        "/service-accounts/",
        json={
            "name": "Service Account 2",
            "phone": "+5511987654323",
            "description": "Second test service",
        },
    )

    response = client.get("/service-accounts/")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 2
    assert data[0]["name"] == "Service Account 1"
    assert data[1]["name"] == "Service Account 2"


def test_update_service_account(client):
    create_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service",
            "phone": "+5511987654322",
            "description": "A test service",
        },
    )
    service_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/service-accounts/{service_id}",
        json={
            "name": "Updated Service",
            "description": "An updated service description",
        },
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["name"] == "Updated Service"
    assert data["description"] == "An updated service description"
    assert data["phone"] == "+5511987654322"


def test_cannot_update_service_account_phone(client):
    create_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service",
            "phone": "+5511987654322",
            "description": "A test service",
        },
    )
    service_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/service-accounts/{service_id}",
        json={"phone": "+5511987654323"},
    )
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res


def test_delete_service_account(client):
    create_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service",
            "phone": "+5511987654322",
            "description": "A test service",
        },
    )
    service_id = create_response.json()["data"]["id"]

    response = client.delete(f"/service-accounts/{service_id}")
    assert response.status_code == 204

    response = client.get(f"/service-accounts/{service_id}")
    assert response.status_code == 404
