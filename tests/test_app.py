import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice tactics",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["first@mergington.edu", "second@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore visual arts",
            "schedule": "Wednesdays",
            "max_participants": 16,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client, activity_data):
    # Arrange
    expected_activities = activity_data

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert activity_data[activity_name]["participants"] == [
        "first@mergington.edu",
        "second@mergington.edu",
        email,
    ]


def test_signup_rejects_duplicate_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "first@mergington.edu"
    original_participants = activity_data[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activity_data[activity_name]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "first@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert activity_data[activity_name]["participants"] == [
        "second@mergington.edu"
    ]


def test_unregister_returns_not_found_for_missing_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    original_participants = activity_data[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_data[activity_name]["participants"] == original_participants


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}