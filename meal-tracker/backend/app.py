import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from data_store import record_meal
from routes.auth import auth_bp
from routes.meals import meals_bp
from routes.users import users_bp
from supabase_client import supabase
from utils.bmi_calc import calc_bmi
from utils.calories_detect import detect_calories
from utils.gamification import calculate_points

_SUPABASE_SUPPORTS_PAYLOAD = True


def _resolve_user_id(value):
    if value is None:
        return "demo"
    candidate = str(value).strip()
    return candidate or "demo"


def _normalize_supabase_row(row):
    payload = row.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = None
    if isinstance(payload, dict):
        return payload
    meal_name = row.get("meal_name")
    calories = row.get("calories")
    created_at = row.get("created_at") or row.get("createdAt") or row.get("inserted_at")
    foods = []
    if meal_name:
        foods.append({"name": meal_name, "calories": calories})
    return {
        "id": row.get("id"),
        "foods": foods,
        "calories": calories,
        "points": row.get("points") or 0,
        "mood": row.get("mood"),
        "notes": row.get("notes"),
        "photo": row.get("photo_url"),
        "calorie_method": row.get("calorie_method", "manual"),
        "calorie_confidence": row.get("calorie_confidence", 0.0),
        "created_at": created_at,
    }


def _maybe_disable_payload(message, insert_payload):
    global _SUPABASE_SUPPORTS_PAYLOAD
    if not _SUPABASE_SUPPORTS_PAYLOAD:
        return False
    if not message or "payload" not in message.lower():
        return False
    insert_payload.pop("payload", None)
    _SUPABASE_SUPPORTS_PAYLOAD = False
    return True

app = Flask(__name__)
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://app.shaysystems.com",
]
CORS(app, resources={r"/*": {"origins": allowed_origins}})

app.register_blueprint(meals_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)

@app.route('/bmi', methods=['POST'])
def bmi():
    data = request.get_json(force=True, silent=True) or {}
    try:
        weight = float(data['weight'])
        height = float(data['height'])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Both numeric weight and height are required."}), 400
    try:
        bmi = calc_bmi(weight, height)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"bmi": bmi})

@app.route('/healthz')
def healthz():
    supabase_url_loaded = bool(os.getenv("SUPABASE_URL"))
    service_key_loaded = bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY"))
    return jsonify({
        "status": "UP",
        "supabase_url": supabase_url_loaded,
        "service_key_loaded": service_key_loaded,
        "supabase_ready": supabase_url_loaded and service_key_loaded,
    })

@app.route('/api/healthz')
def api_health():
    return jsonify({"status": "UP"})


@app.route('/meals', methods=['GET'])
def supabase_meal_list():
    try:
        response = supabase.table("meals").select("*").execute()
    except Exception as exc:
        return jsonify({"error": "Failed to query Supabase.", "details": str(exc)}), 500

    if getattr(response, "error", None):
        error_message = getattr(response.error, "message", str(response.error))
        return jsonify({"error": "Supabase returned an error.", "details": error_message}), 502

    data = response.data or []
    normalized = [_normalize_supabase_row(item) for item in data]
    return jsonify({"count": len(normalized), "meals": normalized})


@app.route('/meals', methods=['POST'])
def supabase_create_meal():
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

    try:
        calories_value = float(payload.get("calories", detection["calories"]))
    except (TypeError, ValueError):
        calories_value = detection["calories"]

    points = calculate_points(calories_value, detection["foods"])

    meal = record_meal(
        foods=detection["foods"],
        calories=calories_value,
        points=points,
        notes=payload.get("notes"),
        mood=payload.get("mood"),
        photo=payload.get("photoUrl") or payload.get("photoData"),
        calorie_method=detection["method"],
        calorie_confidence=detection["confidence"],
    )

    meal_name_raw = payload.get("meal_name")
    meal_name = meal_name_raw.strip() if isinstance(meal_name_raw, str) else meal_name_raw
    calorie_for_storage = int(round(meal["calories"]))
    insert_payload = {
        "user_id": _resolve_user_id(payload.get("user_id")),
        "meal_name": meal_name or detection["foods"][0]["name"] or "Meal",
        "calories": calorie_for_storage,
    }
    if _SUPABASE_SUPPORTS_PAYLOAD:
        insert_payload["payload"] = meal

    try:
        response = supabase.table("meals").insert(insert_payload).execute()
    except Exception as exc:
        error_message = str(exc)
        if _maybe_disable_payload(error_message, insert_payload):
            try:
                response = supabase.table("meals").insert(insert_payload).execute()
            except Exception as final_exc:
                return jsonify({"error": "Failed to insert meal into Supabase.", "details": str(final_exc)}), 500
        else:
            return jsonify({"error": "Failed to insert meal into Supabase.", "details": error_message}), 500

    if getattr(response, "error", None):
        error_message = getattr(response.error, "message", str(response.error))
        if not _maybe_disable_payload(error_message, insert_payload):
            return jsonify({"error": "Supabase returned an error.", "details": error_message}), 502
        try:
            response = supabase.table("meals").insert(insert_payload).execute()
        except Exception as final_exc:
            return jsonify({"error": "Failed to insert meal into Supabase.", "details": str(final_exc)}), 500
        if getattr(response, "error", None):
            final_message = getattr(response.error, "message", str(response.error))
            return jsonify({"error": "Supabase returned an error.", "details": final_message}), 502

    return jsonify({**meal, "calorieExplanation": detection["explanation"]}), 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
