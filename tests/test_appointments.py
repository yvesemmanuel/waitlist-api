import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta, UTC

from app.main import app
from app.database import Base, get_db
from app.models import AppointmentStatus

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


@pytest.fixture
def user_id(client):
    response = client.post(
        "/users/",
        json={"name": "Appointment Test User", "phone": "+5511987654321"},
    )
    return response.json()["id"]


def test_create_appointment(client, user_id):
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    response = client.post(
        "/appointments/",
        json={"user_id": user_id, "appointment_date": tomorrow},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["status"] == AppointmentStatus.ACTIVE
    assert "id" in data


def test_create_duplicate_appointment(client, user_id):
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    client.post(
        "/appointments/",
        json={"user_id": user_id, "appointment_date": tomorrow},
    )

    response = client.post(
        "/appointments/",
        json={"user_id": user_id, "appointment_date": tomorrow},
    )
    assert response.status_code == 400
    assert "already has an active appointment" in response.json()["detail"]


def test_get_appointments_for_day(client, user_id):
    tomorrow = datetime.now(UTC) + timedelta(days=1)
    tomorrow_iso = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    client.post(
        "/appointments/",
        json={"user_id": user_id, "appointment_date": tomorrow_iso},
    )

    response = client.get(f"/appointments/?day={tomorrow_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user_id
    assert data[0]["status"] == AppointmentStatus.ACTIVE


def test_cancel_appointment(client, user_id):
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={"user_id": user_id, "appointment_date": tomorrow},
    )
    appointment_id = create_response.json()["id"]

    response = client.delete(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == appointment_id
    assert data["status"] == AppointmentStatus.CANCELED
