import secrets

from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_USERS = {"admin": "1234"}
_sessions: dict[str, str] = {}


def _bearer_token() -> str | None:
    auth_header = (request.headers.get("Authorization") or "").strip()
    if not auth_header:
        return None
    if " " in auth_header:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() == "bearer":
            return token.strip()
    return auth_header


def _issue_token(username: str) -> str:
    token = secrets.token_hex(16)
    while token in _sessions:
        token = secrets.token_hex(16)
    _sessions[token] = username
    return token


@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json(force=True, silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    if _USERS.get(username) != password:
        return jsonify({"error": "Invalid credentials."}), 401
    token = _issue_token(username)
    return jsonify({"token": token})


@auth_bp.route("/profile", methods=["GET"])
def profile():
    token = _bearer_token()
    if token is None or token not in _sessions:
        return jsonify({"error": "Unauthorized."}), 401
    return jsonify({"username": _sessions[token]})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = _bearer_token()
    if token is None or token not in _sessions:
        return jsonify({"error": "Unauthorized."}), 401
    _sessions.pop(token, None)
    return jsonify({"status": "logged_out"})
