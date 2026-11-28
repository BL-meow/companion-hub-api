from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from .models import User
from .extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be valid JSON."
        }), 400

    if not isinstance(data, dict):
        return jsonify({
            "code": "validation_error",
            "message": "Request body must be a JSON object."
        }), 400

    email = data.get("email")
    password = data.get("password")

    details = {}

    if not isinstance(email, str) or not email.strip():
        details["email"] = "Email is required."
    elif not 3 <= len(email) <= 254:
        details["email"] = "Email must be 3-254 characters."

    if not isinstance(password, str) or not password.strip():
        details["password"] = "Password is required."
    elif len(password) < 8:
        details["password"] = "Password must be at least 8 characters."
    elif len(password) > 128:
        details["password"] = "Password must not exceed 128 characters."

    if details:
        return jsonify({
            "code": "validation_error",
            "message": "Invalid registration data.",
            "details": details
        }), 400

    existing = User.query.filter_by(email=email).first()

    if existing is not None:
        return jsonify({
            "code": "duplicate_email",
            "message": "An account with this email already exists."
        }), 409

    hashed = generate_password_hash(password)

    user = User(email=email, password_hash=hashed)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 201