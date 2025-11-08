from flask import Blueprint, jsonify, request

from data_store import meal_count, meals, record_meal, total_points
from utils.calories_detect import detect_calories
from utils.gamification import (
    calculate_points,
    coaching_tips,
    streak_report,
    summarize_achievements,
    weekly_summary,
)

meals_bp = Blueprint("meals", __name__, url_prefix="/api/meals")


@meals_bp.route("", methods=["GET"])
def list_meals():
    return jsonify({"meals": meals()})


@meals_bp.route("", methods=["POST"])
def create_meal():
    payload = request.get_json(force=True, silent=True) or {}

    foods_payload = payload.get("foods")
    photo_hint = payload.get("photoUrl") or payload.get("photoData") or ""
    detection = detect_calories(
        foods=foods_payload,
        photo_reference=photo_hint,
        nutrition_hints=payload.get("nutritionHints"),
    )

    if not detection["foods"]:
        return jsonify({"error": "Provide at least one food item or a photo reference."}), 400

    calories = float(payload.get("calories", detection["calories"]))
    points = calculate_points(calories, detection["foods"])

    meal = record_meal(
        foods=detection["foods"],
        calories=calories,
        points=points,
        notes=payload.get("notes"),
        mood=payload.get("mood"),
        photo=payload.get("photoUrl") or payload.get("photoData"),
        calorie_method=detection["method"],
        calorie_confidence=detection["confidence"],
    )
    response = jsonify({**meal, "calorieExplanation": detection["explanation"]})
    response.status_code = 201
    return response


@meals_bp.route("/insights", methods=["GET"])
def insights():
    existing_meals = meals()
    summary = weekly_summary(existing_meals)
    achievements = summarize_achievements(existing_meals, summary)
    streaks = streak_report(existing_meals)
    recommendations = coaching_tips(existing_meals, summary)
    return jsonify(
        {
            "weekly": summary,
            "achievements": achievements,
            "points": total_points(),
            "totalMeals": meal_count(),
            "streaks": streaks,
            "recommendations": recommendations,
        }
    )
