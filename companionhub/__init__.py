import os
from flask import Flask, jsonify
from .extensions import db, migrate
from .config import config


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "dev")

    app.config["CONFIG_NAME"] = config_name
    app.config.from_object(config[config_name])

    db.init_app(app)

    from . import models
    migrate.init_app(app, db)

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .companions import companions_bp
    app.register_blueprint(companions_bp)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "code": "bad_request",
            "message": "Invalid request."
        }), 400

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "code": "forbidden",
            "message": "You do not have access to this resource."
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "code": "not_found",
            "message": "Resource not found."
        }), 404

    return app