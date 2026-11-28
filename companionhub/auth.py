from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db
from datetime import datetime, timedelta, timezone
import jwt
from .decorators import require_auth


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


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be a valid JSON object."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "code": "validation_error",
            "message": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({
            "code": "invalid_credentials",
            "message": "Invalid credentials."
        }), 401

    secret = current_app.config["JWT_SECRET_KEY"]
    lifetime = current_app.config["JWT_LIFETIME_SECONDS"]

    exp = datetime.now(timezone.utc) + timedelta(seconds=lifetime)

    payload = {
        "sub": str(user.id),
        "role": "user",
        "exp": exp
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return jsonify({"access_token": token}), 200

@auth_bp.get("/me")
@require_auth
def me():
    user = db.session.get(User, g.current_user_id)

    if user is None:
        return jsonify({
            "code": "unauthorized",
            "message": "User not found."
        }), 401

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 200

@auth_bp.patch("/me")
@require_auth
def update_me():
    user = db.session.get(User, g.current_user_id)

    if user is None:
        return jsonify({
            "code": "unauthorized",
            "message": "User not found."
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be a JSON object."
        }), 400

    if set(data) - {"email"}:
        return jsonify({
            "code": "validation_error",
            "message": "Only email can be updated."
        }), 400

    if "email" in data:
        email = data["email"]

        if not isinstance(email, str) or not 3 <= len(email.strip()) <= 254:
            return jsonify({
                "code": "validation_error",
                "message": "Invalid email."
            }), 400

        email = email.strip()

        existing = User.query.filter_by(email=email).first()

        if existing is not None and existing.id != user.id:
            return jsonify({
                "code": "duplicate_email",
                "message": "Email is already in use."
            }), 409

        user.email = email
        db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }), 200

@auth_bp.get("/admin-test")
@require_auth
def admin_test():
    user = db.session.get(User, g.current_user_id)

    if user is None:
        return jsonify({
            "code": "unauthorized",
            "message": "User not found."
        }), 401

    if user.role != "admin":
        return jsonify({
            "code": "forbidden",
            "message": "Admin access required."
        }), 403

    return jsonify({
        "message": "Welcome, admin!"
    }), 200