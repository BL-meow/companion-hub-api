import os
from flask import Flask
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
    return app