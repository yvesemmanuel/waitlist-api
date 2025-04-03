"""
Appointment routers tests.
"""

from datetime import datetime, timedelta, timezone
from shlex import quote


def test_create_appointment(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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
    assert data["user_phone"] == user_phone
    assert data["service_account_phone"] == service_account_phone
    assert data["status"] == "active"


def test_create_appointment_nonexistent_user(client, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": "+9999999999",
            "service_account_phone": service_account_phone,
            "appointment_date": tomorrow,
        },
    )
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res


def test_create_appointment_nonexistent_service_account(client, user_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": "+9999999999",
            "appointment_date": tomorrow,
        },
    )
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res


def test_get_appointments_for_day(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": tomorrow,
        },
    )
    assert response.status_code == 201

    response = client.get(
        "/appointments/", params={"service_account_phone": service_account_phone}
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert len(data) == 1
    assert res["success"] == True
    assert res["message"] == "Appointments queue retrieved successfully"


def test_get_appointments_filter_by_service_account(
    client, user_phone, service_account_phone, another_service_account_phone
):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 201

    day_after_tomorrow = tomorrow + timedelta(days=1)
    day_after_tomorrow_str = day_after_tomorrow.isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": another_service_account_phone,
            "appointment_date": day_after_tomorrow_str,
        },
    )
    assert response.status_code == 201

    response = client.get(
        "/appointments/", params={"service_account_phone": service_account_phone}
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1

    response = client.get(
        "/appointments/",
        params={"service_account_phone": another_service_account_phone},
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1

    response = client.get(
        "/appointments/",
        params={"service_account_phone": service_account_phone, "day": tomorrow_date},
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 1


def test_get_appointment_by_id(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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
    assert data["user_phone"] == user_phone
    assert data["service_account_phone"] == service_account_phone
    assert "user" in data
    assert "service_account" in data


def test_get_nonexistent_appointment(client):
    response = client.get("/appointments/999")
    assert response.status_code == 404
    res = response.json()
    assert "detail" in res
    assert "not found" in res["detail"].lower()


def test_cancel_appointment(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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


def test_complete_appointment(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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


def test_mark_appointment_no_show(client, user_phone, service_account_phone):
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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
    client, user_phone, service_account_phone, another_service_account_phone
):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": another_service_account_phone,
            "appointment_date": tomorrow_str,
        },
    )
    assert response.status_code == 400
    res = response.json()
    assert "detail" in res
    assert "already exists" in res["detail"]


def test_penalty_calculation(client, user_phone, service_account_phone):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    create_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
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
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": next_day_str,
        },
    )
    assert create_response2.status_code == 201

    new_penalty = create_response2.json()["data"]["penalty"]
    assert new_penalty > initial_penalty


def test_ranked_appointments(
    client, user_phone, second_user_phone, service_account_phone
):
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_date = tomorrow.date().isoformat()

    client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": tomorrow_str,
        },
    )

    client.post(
        "/appointments/",
        json={
            "user_phone": second_user_phone,
            "service_account_phone": service_account_phone,
            "appointment_date": (tomorrow + timedelta(hours=2)).isoformat(),
        },
    )

    response = client.get(
        "/appointments/",
        params={"service_account_phone": service_account_phone, "day": tomorrow_date},
    )
    assert response.status_code == 200
    res = response.json()
    data = res["data"]
    assert res["success"] == True
    assert len(data) == 2


def test_appointment_ranking_with_cancellation_history(client):
    """
    Test the ranking queue system with user cancellation history.

    This test creates 3 users and 1 service account, then:
    1. Creates appointments for User 1 on Day X and cancels/no-shows them
    2. Creates appointments for all 3 users on Day Y (Y > X)
    3. Validates that User 1 is ranked lower than Users 2 and 3 in the queue
    """
    user1_phone = "+5511987654331"
    user2_phone = "+5511987654332"
    user3_phone = "+5511987654333"
    service_phone = "+5511987654340"

    user1_response = client.post(
        "/users/",
        json={"name": "User With History", "phone": user1_phone},
    )
    assert user1_response.status_code == 201

    user2_response = client.post(
        "/users/",
        json={"name": "Reliable User 1", "phone": user2_phone},
    )
    assert user2_response.status_code == 201

    user3_response = client.post(
        "/users/",
        json={"name": "Reliable User 2", "phone": user3_phone},
    )
    assert user3_response.status_code == 201

    service_response = client.post(
        "/service-accounts/",
        json={
            "name": "Test Queue Service",
            "phone": service_phone,
            "description": "Service for testing queue priorities",
        },
    )
    assert service_response.status_code == 201

    day_x = datetime.now(timezone.utc) + timedelta(days=5)
    day_x_str = day_x.isoformat()

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_phone": user1_phone,
            "service_account_phone": service_phone,
            "appointment_date": day_x_str,
            "notes": "Will be cancelled",
        },
    )
    assert appointment1_response.status_code == 201
    appointment1_id = appointment1_response.json()["data"]["id"]

    cancel_response = client.delete(f"/appointments/{appointment1_id}")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == "canceled"

    day_x_plus_1 = day_x + timedelta(days=1)
    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_phone": user1_phone,
            "service_account_phone": service_phone,
            "appointment_date": day_x_plus_1.isoformat(),
            "notes": "Will be no-show",
        },
    )
    assert appointment2_response.status_code == 201
    appointment2_id = appointment2_response.json()["data"]["id"]

    no_show_response = client.put(f"/appointments/{appointment2_id}/no-show")
    assert no_show_response.status_code == 200
    assert no_show_response.json()["data"]["status"] == "no_show"

    day_y = day_x + timedelta(days=7)
    day_y_str = day_y.date().isoformat()

    for user_phone in [user1_phone, user2_phone, user3_phone]:
        appointment_response = client.post(
            "/appointments/",
            json={
                "user_phone": user_phone,
                "service_account_phone": service_phone,
                "appointment_date": (day_y + timedelta(hours=1)).isoformat(),
            },
        )
        assert appointment_response.status_code == 201

    queue_response = client.get(
        "/appointments/",
        params={"service_account_phone": service_phone, "day": day_y_str},
    )
    assert queue_response.status_code == 200
    queue_data = queue_response.json()["data"]
    assert len(queue_data) == 3

    user_positions = {item["user_phone"]: i for i, item in enumerate(queue_data)}
    assert user_positions[user1_phone] > user_positions[user2_phone]
    assert user_positions[user1_phone] > user_positions[user3_phone]


def test_disabled_cancellation_scoring(client):
    """
    Test that a service account can disable cancellation scoring,
    which sets all user scores to 0 regardless of history.
    """
    user_phone = "+5511987654351"
    service_phone = "+5511987654352"

    user_response = client.post(
        "/users/",
        json={"name": "User With History", "phone": user_phone},
    )
    assert user_response.status_code == 201

    service_response = client.post(
        "/service-accounts/",
        json={
            "name": "No Scoring Service",
            "phone": service_phone,
            "description": "Service with disabled cancellation scoring",
            "enable_cancellation_scoring": False,
        },
    )
    assert service_response.status_code == 201

    day_one = datetime.now(timezone.utc) + timedelta(days=5)
    day_two = day_one + timedelta(days=1)

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_phone,
            "appointment_date": day_one.isoformat(),
            "notes": "Will be cancelled",
        },
    )
    assert appointment1_response.status_code == 201
    appointment1_id = appointment1_response.json()["data"]["id"]

    cancel_response = client.delete(f"/appointments/{appointment1_id}")
    assert cancel_response.status_code == 200

    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_phone": user_phone,
            "service_account_phone": service_phone,
            "appointment_date": day_two.isoformat(),
            "notes": "Should have zero penalty",
        },
    )
    assert appointment2_response.status_code == 201
    assert appointment2_response.json()["data"]["penalty"] == 0


def test_appointments_queue_functionality(client):
    """
    Test the queue functionality of the appointments endpoint,
    where service_account_phone is mandatory and day is optional.
    Verifies that appointments are ranked by penalty and creation time.
    """
    service_phone = "+1234567890"
    user1_phone = "+1111111111"
    user2_phone = "+2222222222"
    user3_phone = "+3333333333"

    service_response = client.post(
        "/service-accounts/",
        json={
            "name": "Queue Test Service",
            "phone": service_phone,
            "owner_name": "Queue Owner",
            "address": "123 Queue St",
        },
    )
    assert service_response.status_code == 201

    user1_response = client.post(
        "/users/",
        json={"name": "User One", "phone": user1_phone},
    )
    assert user1_response.status_code == 201

    user2_response = client.post(
        "/users/",
        json={"name": "User Two", "phone": user2_phone},
    )
    assert user2_response.status_code == 201

    user3_response = client.post(
        "/users/",
        json={"name": "User Three", "phone": user3_phone},
    )
    assert user3_response.status_code == 201

    today = datetime.now(timezone.utc)
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.date().isoformat()

    appointment1_response = client.post(
        "/appointments/",
        json={
            "user_phone": user1_phone,
            "service_account_phone": service_phone,
            "appointment_date": tomorrow.isoformat(),
            "notes": "First appointment",
        },
    )
    assert appointment1_response.status_code == 201

    appointment2_response = client.post(
        "/appointments/",
        json={
            "user_phone": user2_phone,
            "service_account_phone": service_phone,
            "appointment_date": (tomorrow + timedelta(hours=1)).isoformat(),
            "notes": "Second appointment",
        },
    )
    assert appointment2_response.status_code == 201

    appointment3_response = client.post(
        "/appointments/",
        json={
            "user_phone": user3_phone,
            "service_account_phone": service_phone,
            "appointment_date": (tomorrow + timedelta(hours=2)).isoformat(),
            "notes": "Third appointment",
        },
    )
    assert appointment3_response.status_code == 201

    queue_response = client.get(
        "/appointments/",
        params={"service_account_phone": service_phone, "day": tomorrow_str},
    )
    assert queue_response.status_code == 200
    queue_data = queue_response.json()["data"]
    assert len(queue_data) == 3
