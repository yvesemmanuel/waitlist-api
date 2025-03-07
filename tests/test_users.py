import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["phone"] == "+5511987654321"
    assert "id" in data


def test_create_user_with_invalid_phone(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "123456789"},
    )
    assert response.status_code == 422
    assert "Phone must be in the format" in response.json()["detail"][0]["msg"]


def test_get_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["phone"] == "+5511987654321"
    assert data["id"] == user_id


def test_update_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["id"]

    response = client.put(
        f"/users/{user_id}",
        json={"name": "Updated Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test User"
    assert data["phone"] == "+5511987654321"


def test_delete_user(client):
    create_response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
