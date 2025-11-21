import pytest
from flask import Flask

from data_store import _user_profile
from routes.users import users_bp


@pytest.fixture(autouse=True)
def reset_profile():
    _user_profile.clear()
    _user_profile.update({"height": None, "weight": None})
    yield
    _user_profile.clear()
    _user_profile.update({"height": None, "weight": None})


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(users_bp)
    return app.test_client()


def test_profile_returns_estimated_calories(client):
    response = client.put(
        "/api/users/profile",
        json={"height": 170, "weight": 68, "gender": "male", "age": 30, "activityLevel": "moderate"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["estimatedCalories"] == 2157
    assert data["bmi"] is not None


def test_profile_returns_none_when_missing_data(client):
    response = client.get("/api/users/profile")
    data = response.get_json()

    assert response.status_code == 200
    assert data["estimatedCalories"] is None
    assert data["profile"]["gender"] is None
