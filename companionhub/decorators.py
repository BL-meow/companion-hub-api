from flask import jsonify, request, current_app, g
from functools import wraps
import jwt


def require_auth(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "code": "unauthorized",
                "message": "Missing or invalid authorization header."
            }), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
                options={"require": ["sub", "exp"]}
            )

            g.current_user_id = int(payload["sub"])

        except jwt.ExpiredSignatureError:
            return jsonify({
                "code": "invalid_token",
                "message": "Token has expired."
            }), 401

        except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
            return jsonify({
                "code": "invalid_token",
                "message": "Invalid token."
            }), 401

        return view(*args, **kwargs)

    return wrapper