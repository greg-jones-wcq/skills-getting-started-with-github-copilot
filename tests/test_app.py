import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    app_module.activities.clear()
    app_module.activities.update(
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
            },
            "Gym Class": {
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"],
            },
        }
    )
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"Chess Club", "Programming Class", "Gym Class"}
    assert body["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant(client):
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_removes_participant(client):
    response = client.delete("/activities/Chess Club/signup?email=daniel@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered daniel@mergington.edu from Chess Club"}
    assert "daniel@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    response = client.delete("/activities/Chess Club/signup?email=missing@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_invalid_activity_returns_404(client):
    response = client.get("/activities/DoesNotExist")

    assert response.status_code == 404
