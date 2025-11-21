import pytest
from flask import Flask

from data_store import _meals
from routes.meals import meals_bp


@pytest.fixture(autouse=True)
def reset_meals():
    _meals.clear()
    yield
    _meals.clear()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(meals_bp)
    return app.test_client()


def test_create_meal_rejects_non_numeric_calories(client):
    response = client.post(
        "/api/meals",
        json={"foods": [{"name": "apple"}], "calories": "not-a-number"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Calories must be a number."}
