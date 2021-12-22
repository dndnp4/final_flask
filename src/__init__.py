"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from ddtrace import patch_all
from .encrypt import *

db = SQLAlchemy()
# patch_all()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.FlaskConfig")

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes

        db.create_all()  # Create database tables for our data models

        return app
