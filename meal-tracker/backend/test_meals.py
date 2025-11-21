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


def test_create_meal_accepts_ingredients_and_meal_type(client):
    response = client.post(
        "/api/meals",
        json={"ingredients": "apple, banana", "mealType": "breakfast"},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["meal_type"] == "breakfast"
    assert body["ingredients"] == ["apple", "banana"]


def test_create_meal_accepts_meal_type_alone(client):
    response = client.post(
        "/api/meals",
        json={"mealType": "lunch"},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["meal_type"] == "lunch"
    assert body["foods"][0]["name"] == "lunch"
