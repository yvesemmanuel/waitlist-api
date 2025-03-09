import pytest

from app.main import app


def test_create_regular_user(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    assert response.status_code == 201
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert res["message"] == "User created successfully"
    assert data["name"] == "Test User"
    assert data["phone"] == "+5511987654321"
    assert "id" in data


def test_create_user_with_invalid_phone(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "123456789"},
    )
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res


def test_get_regular_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["name"] == "Test User"
    assert data["phone"] == "+5511987654321"
    assert "appointments" in data


def test_get_all_users(client):
    client.post(
        "/users/",
        json={"name": "Regular User", "phone": "+5511987654321"},
    )

    client.post(
        "/users/",
        json={"name": "Another User", "phone": "+5511987654322"},
    )

    response = client.get("/users/")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 2
    assert {"Regular User", "Another User"} == {data[0]["name"], data[1]["name"]}


def test_update_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/users/{user_id}",
        json={"name": "Updated User", "email": "test@example.com"},
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["name"] == "Updated User"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "+5511987654321"


def test_cannot_update_phone(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/users/{user_id}",
        json={"phone": "+5511987654322"},
    )
    assert response.status_code == 422
    res = response.json()
    assert "detail" in res


def test_delete_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
