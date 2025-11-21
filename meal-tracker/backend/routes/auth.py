import hashlib
import os
import time

import jwt
from flask import Blueprint, jsonify, request
from jwt import InvalidTokenError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_USERS: dict[str, str] = {}
_API_SECRET = os.getenv("API_SECRET")
_JWT_SECRET = os.getenv("JWT_SECRET")
_TOKEN_TTL_SECONDS = 60 * 60 * 24


def _bearer_token() -> str | None:
    auth_header = (request.headers.get("Authorization") or "").strip()
    if not auth_header:
        return None
    if " " in auth_header:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() == "bearer":
            return token.strip()
    return auth_header


def _api_secret_valid() -> bool:
    candidate = _bearer_token() or request.headers.get("X-API-Key")
    return bool(_API_SECRET and candidate == _API_SECRET)


def _hash_password(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _issue_jwt(email: str) -> str:
    if not _JWT_SECRET:
        raise RuntimeError("Server misconfigured: missing JWT_SECRET")
    payload = {
        "sub": email,
        "exp": int(time.time() + _TOKEN_TTL_SECONDS),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def _decode_jwt(token: str):
    if not _JWT_SECRET:
        return None, jsonify({"error": "Server misconfigured: missing JWT_SECRET"}), 500
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub"), None, None
    except InvalidTokenError:
        return None, jsonify({"error": "Unauthorized"}), 401


@auth_bp.route("/signup", methods=["POST"])
def signup():
    if not _API_SECRET:
        return jsonify({"error": "Server misconfigured: missing API_SECRET"}), 500
    if not _api_secret_valid():
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True, silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    if email in _USERS:
        return jsonify({"error": "User already exists."}), 409

    _USERS[email] = _hash_password(password)
    return jsonify({"status": "created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    if not _API_SECRET:
        return jsonify({"error": "Server misconfigured: missing API_SECRET"}), 500
    if not _api_secret_valid():
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True, silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    stored_hash = _USERS.get(email)
    if not stored_hash or stored_hash != _hash_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    try:
        token = _issue_jwt(email)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify({"token": token})


@auth_bp.route("/profile", methods=["GET"])
def profile():
    token = _bearer_token()
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    user_email, error_response, status = _decode_jwt(token)
    if error_response:
        return error_response, status
    return jsonify({"email": user_email})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Stateless JWT session; respond OK for client compatibility.
    return jsonify({"status": "logged_out"})
