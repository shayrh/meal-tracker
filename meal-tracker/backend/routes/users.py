from flask import Blueprint, jsonify, request

from data_store import update_profile, user_profile
from utils.bmi_calc import calc_bmi

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _profile_payload():
    profile = user_profile()
    height = profile.get("height")
    weight = profile.get("weight")
    try:
        bmi = calc_bmi(weight, height) if height and weight else None
    except ValueError:
        bmi = None
    return profile, bmi


@users_bp.route("/profile", methods=["GET"])
def get_profile():
    profile, bmi = _profile_payload()
    return jsonify({"profile": profile, "bmi": bmi})


@users_bp.route("/profile", methods=["PUT"])
def put_profile():
    payload = request.get_json(force=True, silent=True) or {}
    height = payload.get("height")
    weight = payload.get("weight")
    try:
        height_value = float(height) if height is not None else None
        weight_value = float(weight) if weight is not None else None
    except (TypeError, ValueError):
        return jsonify({"error": "Height and weight must be numbers."}), 400
    profile = update_profile(height=height_value, weight=weight_value)
    try:
        bmi = calc_bmi(profile["weight"], profile["height"]) if profile.get("height") and profile.get("weight") else None
    except ValueError:
        bmi = None
    return jsonify({"profile": profile, "bmi": bmi})


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
