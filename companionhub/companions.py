from flask import Blueprint, jsonify, request, g
from .models import Companion
from .extensions import db
from .auth import require_auth

companions_bp = Blueprint(
    "companions",
    __name__,
    url_prefix="/api/companions"
)


@companions_bp.post("")
@require_auth
def create_companion():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be a JSON object."
        }), 400

    name = data.get("name")
    personality = data.get("personality")

    details = {}

    if not isinstance(name, str) or not name.strip():
        details["name"] = "Name is required."
    elif len(name.strip()) > 100:
        details["name"] = "Name must not exceed 100 characters."

    if not isinstance(personality, str) or not personality.strip():
        details["personality"] = "Personality is required."

    for field in ("backstory", "appearance", "greeting"):
        value = data.get(field)

        if value is not None and not isinstance(value, str):
            details[field] = "Must be a string."

    is_public = data.get("is_public", False)

    if not isinstance(is_public, bool):
        details["is_public"] = "Must be a boolean."

    if details:
        return jsonify({
            "code": "validation_error",
            "message": "Invalid companion data.",
            "details": details
        }), 400

    companion = Companion(
        user_id=g.current_user_id,
        name=name.strip(),
        personality=personality.strip(),
        backstory=data.get("backstory"),
        appearance=data.get("appearance"),
        greeting=data.get("greeting"),
        is_public=is_public
    )

    db.session.add(companion)
    db.session.commit()

    return jsonify({
        "id": companion.id,
        "user_id": companion.user_id,
        "name": companion.name,
        "personality": companion.personality,
        "backstory": companion.backstory,
        "appearance": companion.appearance,
        "greeting": companion.greeting,
        "is_public": companion.is_public,
        "created_at": companion.created_at.isoformat(),
        "updated_at": companion.updated_at.isoformat()
    }), 201

@companions_bp.get("")
@require_auth
def list_companions():
    companions = Companion.query.filter_by(
        user_id=g.current_user_id
    ).all()

    return jsonify([
        {
            "id": companion.id,
            "user_id": companion.user_id,
            "name": companion.name,
            "personality": companion.personality,
            "backstory": companion.backstory,
            "appearance": companion.appearance,
            "greeting": companion.greeting,
            "is_public": companion.is_public,
            "created_at": companion.created_at.isoformat(),
            "updated_at": companion.updated_at.isoformat()
        }
        for companion in companions
    ]), 200

@companions_bp.get("/<int:companion_id>")
@require_auth
def get_companion(companion_id):
    companion = Companion.query.filter_by(
    id=companion_id,
    user_id=g.current_user_id
).first()

    if companion is None:
        return jsonify({
            "code": "not_found",
            "message": "Companion not found."
        }), 404

    return jsonify({
        "id": companion.id,
        "user_id": companion.user_id,
        "name": companion.name,
        "personality": companion.personality,
        "backstory": companion.backstory,
        "appearance": companion.appearance,
        "greeting": companion.greeting,
        "is_public": companion.is_public,
        "created_at": companion.created_at.isoformat(),
        "updated_at": companion.updated_at.isoformat()
    }), 200

