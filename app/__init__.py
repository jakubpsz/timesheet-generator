
"""
Application factory for the Flask app.
"""
from flask import Flask
from .config import load_config

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="main/templates/htm", static_folder="main/static", static_url_path="/static")

    # Load configuration
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)

    # Register blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
