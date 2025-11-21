from flask import Blueprint, jsonify, request

from data_store import update_profile, user_profile
from utils.bmi_calc import calc_bmi

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _profile_payload():
    profile = user_profile()
    height = profile.get("height")
    weight = profile.get("weight")
    gender = (profile.get("gender") or "").lower() or None
    activity_level = (profile.get("activity_level") or "").lower() or None
    age = profile.get("age")
    try:
        bmi = calc_bmi(weight, height) if height and weight else None
    except ValueError:
        bmi = None
    return profile, bmi, _estimated_calories(weight, height, gender, age, activity_level)


def _activity_factor(level: str) -> float:
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }.get(level or "", 1.35)


def _estimated_calories(weight, height, gender=None, age=None, activity_level=None):
    """
    Rough daily maintenance calorie estimate using Mifflin-St Jeor and activity factor.
    Defaults: gender-neutral constant, age 30, light/moderate activity if not supplied.
    """
    try:
        weight_val = float(weight)
        height_val = float(height)
        age_val = float(age) if age is not None else 30
    except (TypeError, ValueError):
        return None
    if weight_val <= 0 or height_val <= 0 or age_val <= 0:
        return None
    gender_const = 5 if (gender or "").lower() == "male" else -161 if (gender or "").lower() == "female" else 0
    bmr = 10 * weight_val + 6.25 * height_val - 5 * age_val + gender_const
    estimate = int(round(bmr * _activity_factor(activity_level)))
    return max(1200, estimate)


@users_bp.route("/profile", methods=["GET"])
def get_profile():
    profile, bmi, estimated = _profile_payload()
    return jsonify({"profile": profile, "bmi": bmi, "estimatedCalories": estimated})


@users_bp.route("/profile", methods=["PUT"])
def put_profile():
    payload = request.get_json(force=True, silent=True) or {}
    height = payload.get("height")
    weight = payload.get("weight")
    gender = (payload.get("gender") or "").strip().lower() or None
    age = payload.get("age")
    activity_level = (payload.get("activityLevel") or payload.get("activity_level") or "").strip().lower() or None
    try:
        height_value = float(height) if height is not None else None
        weight_value = float(weight) if weight is not None else None
        age_value = float(age) if age is not None else None
    except (TypeError, ValueError):
        return jsonify({"error": "Height and weight must be numbers."}), 400
    profile = update_profile(
        height=height_value,
        weight=weight_value,
        gender=gender,
        age=age_value,
        activity_level=activity_level,
    )
    try:
        bmi = calc_bmi(profile["weight"], profile["height"]) if profile.get("height") and profile.get("weight") else None
    except ValueError:
        bmi = None
    estimated = _estimated_calories(
        profile.get("weight"),
        profile.get("height"),
        profile.get("gender"),
        profile.get("age"),
        profile.get("activity_level"),
    )
    return jsonify({"profile": profile, "bmi": bmi, "estimatedCalories": estimated})


@users_bp.route("/bmi", methods=["POST"])
def compute_bmi():
    payload = request.get_json(force=True, silent=True) or {}
    weight = payload.get("weight")
    height = payload.get("height")
    if weight is None or height is None:
        return jsonify({"error": "Both weight and height are required."}), 400
    try:
        weight_value = float(weight)
        height_value = float(height)
    except (TypeError, ValueError):
        return jsonify({"error": "Height and weight must be numbers."}), 400
    try:
        bmi = calc_bmi(weight_value, height_value)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"bmi": bmi})
