from flask import Blueprint, jsonify, request, g, abort
from .models import Companion
from .extensions import db
from .auth import require_auth
from .validators import validate_companion_body

companions_bp = Blueprint(
    "companions",
    __name__,
    url_prefix="/api/companions"
)


@companions_bp.post("")
@require_auth
def create_companion():
    data = request.get_json(silent=True)

    normalized_data, details, error_code = validate_companion_body(data)

    if error_code == "invalid_json":
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be a JSON object."
        }), 400

    if error_code == "validation_error":
        return jsonify({
            "code": "validation_error",
            "message": "Invalid companion data.",
            "details": details
        }), 400

    companion = Companion(
        user_id=g.current_user_id,
        **normalized_data
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
    companion = db.session.get(Companion, companion_id)

    if companion is None:
        abort(404)

    if companion.user_id != g.current_user_id:
        abort(403)

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

@companions_bp.patch("/<int:companion_id>")
@require_auth
def update_companion(companion_id):
    companion = db.session.get(Companion, companion_id)

    if companion is None:
        abort(404)

    if companion.user_id != g.current_user_id:
        abort(403)

    data = request.get_json(silent=True)

    normalized_data, details, error_code = validate_companion_body(
        data, partial=True
    )

    if error_code == "invalid_json":
        return jsonify({
            "code": "invalid_json",
            "message": "Request body must be a JSON object."
        }), 400

    if error_code == "validation_error":
        return jsonify({
            "code": "validation_error",
            "message": "Invalid companion data.",
            "details": details
        }), 400

    for field, value in normalized_data.items():
        setattr(companion, field, value)

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
    }), 200


@companions_bp.delete("/<int:companion_id>")
@require_auth
def delete_companion(companion_id):
    companion = Companion.query.filter_by(
        id=companion_id,
        user_id=g.current_user_id
    ).first()

    if companion is None:
        return jsonify({
            "code": "not_found",
            "message": "Companion not found."
        }), 404

    db.session.delete(companion)
    db.session.commit()

    return "", 204

