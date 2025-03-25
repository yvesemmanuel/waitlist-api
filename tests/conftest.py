import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.models.database import get_db


@pytest.fixture(scope="session")
def test_engine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def test_session_local(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def override_get_db(test_session_local):
    def _override_get_db():
        try:
            db = test_session_local()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_engine, override_get_db):
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def user_id(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "phone": "+5511987654321"},
    )
    return response.json()["data"]["id"]


@pytest.fixture
def second_user_id(client):
    response = client.post(
        "/users/",
        json={"name": "Second User", "phone": "+5511987654322"},
    )
    return response.json()["data"]["id"]


@pytest.fixture
def service_account_id(client):
    response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Service",
            "phone": "+5511987654323",
            "description": "A test service",
        },
    )
    return response.json()["data"]["id"]


@pytest.fixture
def another_service_account_id(client):
    response = client.post(
        "/service-accounts/",
        json={
            "name": "Another Service",
            "phone": "+5511987654324",
            "description": "Another test service",
        },
    )
    return response.json()["data"]["id"]
