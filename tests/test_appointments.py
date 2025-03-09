import pytest
from datetime import datetime, timedelta, timezone
import time

from app.main import app


def test_create_appointment(client, user_id, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
            "duration_minutes": 30,
            "notes": "Test appointment",
        },
    )
    assert response.status_code == 201
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert res["message"] == "Appointment created successfully"
    assert data["user_id"] == user_id
    assert data["service_account_id"] == service_account_id
    assert data["status"] == "active"
    assert "id" in data


def test_create_appointment_nonexistent_user(client, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": 999,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
        },
    )
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res


def test_create_appointment_nonexistent_service_account(client, user_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": 999,
            "appointment_date": tomorrow,
        },
    )
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res


def test_get_appointments_for_day(client, user_id, service_account_id):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 201

    response = client.get(
        f"/appointments/?service_account_id={service_account_id}&day={tomorrow_date}"
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert res["message"] == "Appointments queue retrieved successfully"
    assert len(data) == 1
    assert data[0]["user_id"] == user_id
    assert data[0]["service_account_id"] == service_account_id


def test_get_appointments_filter_by_service_account(
    client, user_id, service_account_id, another_service_account_id
):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 201

    day_after_tomorrow = tomorrow + timedelta(days=1)
    day_after_tomorrow_str = day_after_tomorrow.isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": another_service_account_id,
            "appointment_date": day_after_tomorrow_str,
        },
    )
    assert response.status_code == 201

    response = client.get(f"/appointments/?service_account_id={service_account_id}")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1
    assert data[0]["service_account_id"] == service_account_id

    response = client.get(
        f"/appointments/?service_account_id={another_service_account_id}"
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1
    assert data[0]["service_account_id"] == another_service_account_id

    response = client.get(
        f"/appointments/?service_account_id={service_account_id}&day={tomorrow_date}"
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1
    assert data[0]["service_account_id"] == service_account_id


def test_get_appointment_by_id(client, user_id, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
        },
    )
    appointment_id = create_response.json()["data"]["id"]

    response = client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["id"] == appointment_id
    assert data["user_id"] == user_id
    assert data["service_account_id"] == service_account_id
    assert "user" in data
    assert "service_account" in data


def test_get_nonexistent_appointment(client):
    response = client.get("/appointments/999")
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res
    assert "not found" in res["detail"].lower()


def test_cancel_appointment(client, user_id, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
        },
    )
    appointment_id = create_response.json()["data"]["id"]

    response = client.delete(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["id"] == appointment_id
    assert data["status"] == "canceled"


def test_complete_appointment(client, user_id, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
        },
    )
    appointment_id = create_response.json()["data"]["id"]

    response = client.put(f"/appointments/{appointment_id}/complete")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["id"] == appointment_id
    assert data["status"] == "completed"


def test_mark_appointment_no_show(client, user_id, service_account_id):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow,
        },
    )
    appointment_id = create_response.json()["data"]["id"]

    response = client.put(f"/appointments/{appointment_id}/no-show")
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert data["id"] == appointment_id
    assert data["status"] == "no_show"


def test_user_only_one_appointment_per_day(
    client, user_id, service_account_id, another_service_account_id
):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": another_service_account_id,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 400
    res = response.json()
    assert "detail" in res
    assert "already have an appointment scheduled for this day" in res["detail"]


def test_penalty_calculation(client, user_id, service_account_id):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow_str,
        },
    )
    appointment_id = create_response.json()["data"]["id"]
    initial_penalty = create_response.json()["data"]["penalty"]
    assert initial_penalty == 0.0

    client.delete(f"/appointments/{appointment_id}")

    next_day = datetime.now(timezone.utc) + timedelta(days=3)
    next_day_str = next_day.isoformat()

    create_response2 = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": next_day_str,
        },
    )
    assert create_response2.status_code == 201

    new_penalty = create_response2.json()["data"]["penalty"]
    assert new_penalty > initial_penalty


def test_ranked_appointments(client, user_id, second_user_id, service_account_id):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_account_id,
            "appointment_date": tomorrow_str,
        },
    )

    client.post(
        "/appointments/",
        json={
            "user_id": second_user_id,
            "service_account_id": service_account_id,
            "appointment_date": (tomorrow + timedelta(hours=2)).isoformat(),
        },
    )

    response = client.get(
        f"/appointments/?service_account_id={service_account_id}&day={tomorrow_date}"
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) >= 1
    if len(data) > 1:
        assert data[0]["penalty"] <= data[1]["penalty"]


def test_appointment_ranking_with_cancellation_history(client):
    """
    Test the ranking queue system with user cancellation history.

    This test creates 3 users and 1 service account, then:
    1. Creates appointments for User 1 on Day X and cancels/no-shows them
    2. Creates appointments for all 3 users on Day Y (Y > X)
    3. Validates that User 1 is ranked lower than Users 2 and 3 in the queue
    """
    user1_response = client.post(
        "/users/",
        json={"name": "User With History", "phone": "+5511987654331"},
    )
    user1_id = user1_response.json()["data"]["id"]

    user2_response = client.post(
        "/users/",
        json={"name": "Reliable User 1", "phone": "+5511987654332"},
    )
    user2_id = user2_response.json()["data"]["id"]

    user3_response = client.post(
        "/users/",
        json={"name": "Reliable User 2", "phone": "+5511987654333"},
    )
    user3_id = user3_response.json()["data"]["id"]

    service_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Queue Service",
            "phone": "+5511987654340",
            "description": "Service for testing queue priorities",
        },
    )
    service_id = service_response.json()["data"]["id"]

    day_x = datetime.now(timezone.utc) + timedelta(days=5)
    day_x_str = day_x.isoformat()

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": day_x_str,
            "notes": "Will be cancelled",
        },
    )
    appointment1_id = appointment1_response.json()["data"]["id"]
    client.delete(f"/appointments/{appointment1_id}")

    day_x_plus_1 = day_x + timedelta(days=1)
    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": day_x_plus_1.isoformat(),
            "notes": "Will be no-show",
        },
    )
    appointment2_id = appointment2_response.json()["data"]["id"]
    client.put(f"/appointments/{appointment2_id}/no-show")

    day_y = datetime.now(timezone.utc) + timedelta(days=10)
    day_y_str = day_y.isoformat()
    day_y_date = day_y.date().isoformat()

    client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": day_y_str,
            "notes": "User with cancellation history",
        },
    )

    client.post(
        "/appointments/",
        json={
            "user_id": user2_id,
            "service_account_id": service_id,
            "appointment_date": day_y_str,
            "notes": "Reliable user 1",
        },
    )

    client.post(
        "/appointments/",
        json={
            "user_id": user3_id,
            "service_account_id": service_id,
            "appointment_date": day_y_str,
            "notes": "Reliable user 2",
        },
    )

    response = client.get(
        f"/appointments/?service_account_id={service_id}&day={day_y_date}"
    )
    assert response.status_code == 200
    res = response.json()
    appointments = res["data"]

    assert len(appointments) == 3

    first_ranked_user = appointments[0]
    second_ranked_user = appointments[1]
    third_ranked_user = appointments[2]

    print("\nAppointment Queue Rankings:")
    print(
        f"1. User ID: {first_ranked_user['user_id']}, Penalty: {first_ranked_user['penalty']}"
    )
    print(
        f"2. User ID: {second_ranked_user['user_id']}, Penalty: {second_ranked_user['penalty']}"
    )
    print(
        f"3. User ID: {third_ranked_user['user_id']}, Penalty: {third_ranked_user['penalty']}"
    )
    print(f"User with cancellation history (User1): {user1_id}")
    print(f"Reliable users: {user2_id}, {user3_id}")

    assert first_ranked_user["user_id"] != user1_id
    assert second_ranked_user["user_id"] != user1_id
    assert third_ranked_user["user_id"] == user1_id

    reliable_user_ids = {user2_id, user3_id}
    assert first_ranked_user["user_id"] in reliable_user_ids
    assert second_ranked_user["user_id"] in reliable_user_ids

    assert first_ranked_user["penalty"] <= second_ranked_user["penalty"]
    assert second_ranked_user["penalty"] < third_ranked_user["penalty"]


def test_disabled_cancellation_scoring(client):
    """
    Test that a service account can disable cancellation scoring,
    which sets all user scores to 0 regardless of history.
    """
    user_response = client.post(
        "/users/",
        json={"name": "User With History", "phone": "+5511987654351"},
    )
    user_id = user_response.json()["data"]["id"]

    service_response = client.post(
        "/service-accounts/",
        json={
            "name": "No Scoring Service",
            "phone": "+5511987654352",
            "description": "Service with disabled cancellation scoring",
            "enable_cancellation_scoring": False,
        },
    )
    service_id = service_response.json()["data"]["id"]

    day_one_service1 = datetime.now(timezone.utc) + timedelta(days=5)
    day_two_service1 = day_one_service1 + timedelta(days=1)

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_id,
            "appointment_date": day_one_service1.isoformat(),
            "notes": "Will be cancelled",
        },
    )
    appointment1_id = appointment1_response.json()["data"]["id"]

    assert appointment1_response.json()["data"]["penalty"] == 0.0

    client.delete(f"/appointments/{appointment1_id}")

    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": service_id,
            "appointment_date": day_two_service1.isoformat(),
            "notes": "Score should still be 0",
        },
    )

    assert appointment2_response.json()["data"]["penalty"] == 0.0

    weighted_service_response = client.post(
        "/service-accounts/",
        json={
            "name": "Custom Weights Service",
            "phone": "+5511987654353",
            "description": "Service with custom weights",
            "enable_cancellation_scoring": True,
            "cancellation_weight": 0.5,
            "no_show_weight": 3.0,
        },
    )
    weighted_service_id = weighted_service_response.json()["data"]["id"]

    day_one_service2 = datetime.now(timezone.utc) + timedelta(days=10)
    day_two_service2 = day_one_service2 + timedelta(days=1)

    appointment3_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": weighted_service_id,
            "appointment_date": day_one_service2.isoformat(),
            "notes": "For weighted service",
        },
    )
    appointment3_id = appointment3_response.json()["data"]["id"]

    assert appointment3_response.json()["data"]["penalty"] == 0.0

    client.delete(f"/appointments/{appointment3_id}")

    appointment4_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": weighted_service_id,
            "appointment_date": day_two_service2.isoformat(),
            "notes": "Score should reflect custom weights",
        },
    )

    appointment4_data = appointment4_response.json()["data"]
    score = appointment4_data["penalty"]
    assert score > 0.0, (
        "Score should be greater than 0 for a service with enabled scoring"
    )

    default_service_response = client.post(
        "/service-accounts/",
        json={
            "name": "Default Weights Service",
            "phone": "+5511987654354",
            "description": "Service with default weights",
        },
    )
    default_service_id = default_service_response.json()["data"]["id"]

    day_one_service3 = datetime.now(timezone.utc) + timedelta(days=15)
    day_two_service3 = day_one_service3 + timedelta(days=1)

    appointment5_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": default_service_id,
            "appointment_date": day_one_service3.isoformat(),
            "notes": "For default weighted service",
        },
    )
    appointment5_id = appointment5_response.json()["data"]["id"]
    client.delete(f"/appointments/{appointment5_id}")

    appointment6_response = client.post(
        "/appointments/",
        json={
            "user_id": user_id,
            "service_account_id": default_service_id,
            "appointment_date": day_two_service3.isoformat(),
            "notes": "Score should reflect default weights",
        },
    )

    appointment6_data = appointment6_response.json()["data"]
    default_score = appointment6_data["penalty"]
    assert default_score > 0.0, (
        "Score should be greater than 0 for a service with default scoring"
    )

    assert score <= default_score, (
        "Custom weighted service with lower cancellation_weight should have lower or equal score"
    )


def test_appointments_queue_functionality(client):
    """
    Test the queue functionality of the appointments endpoint,
    where service_account_id is mandatory and day is optional.
    Verifies that appointments are ranked by penalty and creation time.
    """
    service_account_response = client.post(
        "/service-accounts/",
        json={
            "name": "Queue Test Service",
            "phone": "+1234567890",
            "owner_name": "Queue Owner",
            "address": "123 Queue St",
        },
    )
    service_id = service_account_response.json()["data"]["id"]

    user1_response = client.post(
        "/users/",
        json={"name": "User One", "phone": "+1111111111"},
    )
    user1_id = user1_response.json()["data"]["id"]

    user2_response = client.post(
        "/users/",
        json={"name": "User Two", "phone": "+2222222222"},
    )
    user2_id = user2_response.json()["data"]["id"]

    user3_response = client.post(
        "/users/",
        json={"name": "User Three", "phone": "+3333333333"},
    )
    user3_id = user3_response.json()["data"]["id"]

    past_date = datetime.now(timezone.utc) - timedelta(days=7)

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": past_date.isoformat(),
        },
    )
    appointment1_id = appointment1_response.json()["data"]["id"]
    client.put(f"/appointments/{appointment1_id}/no-show")

    past_date2 = datetime.now(timezone.utc) - timedelta(days=3)
    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": past_date2.isoformat(),
        },
    )
    appointment2_id = appointment2_response.json()["data"]["id"]
    client.put(f"/appointments/{appointment2_id}/no-show")

    future_date = datetime.now(timezone.utc) + timedelta(days=5)
    future_date_str = future_date.isoformat()

    client.post(
        "/appointments/",
        json={
            "user_id": user1_id,
            "service_account_id": service_id,
            "appointment_date": future_date_str,
            "notes": "User with highest penalty",
        },
    )

    time.sleep(0.1)

    client.post(
        "/appointments/",
        json={
            "user_id": user3_id,
            "service_account_id": service_id,
            "appointment_date": future_date_str,
            "notes": "User with no penalty, middle creation time",
        },
    )

    time.sleep(0.1)

    client.post(
        "/appointments/",
        json={
            "user_id": user2_id,
            "service_account_id": service_id,
            "appointment_date": future_date_str,
            "notes": "User with no penalty, latest creation time",
        },
    )

    response = client.get(f"/appointments/?service_account_id={service_id}")
    assert response.status_code == 200
    res = response.json()
    appointments = res["data"]

    assert len(appointments) == 3
    assert res["success"] == True
    assert res["message"] == "Appointments queue retrieved successfully"

    assert appointments[0]["user_id"] == user3_id
    assert appointments[1]["user_id"] == user2_id
    assert appointments[2]["user_id"] == user1_id

    future_date_only = future_date.date().isoformat()
    response = client.get(
        f"/appointments/?service_account_id={service_id}&day={future_date_only}"
    )
    assert response.status_code == 200
    res = response.json()
    appointments = res["data"]

    assert len(appointments) == 3
    assert appointments[0]["user_id"] == user3_id
    assert appointments[1]["user_id"] == user2_id
    assert appointments[2]["user_id"] == user1_id

    response = client.get(
        f"/appointments/?service_account_id={service_id}&user_id={user1_id}"
    )
    assert response.status_code == 200
    res = response.json()
    appointments = res["data"]

    assert len(appointments) == 1
    assert appointments[0]["user_id"] == user1_id

    response = client.get("/appointments/")
    assert response.status_code == 422
