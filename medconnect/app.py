import os
from flask import Flask, redirect, url_for
from dotenv import load_dotenv

from config.settings import get_config
from database.database import init_db
from api.ivr_routes import ivr_bp
from api.admin_routes import admin_bp
from web.views import web_bp
from utils.logger import setup_logger


def create_app():
    """
    Application Factory Pattern
    """

    # Load environment variables
    load_dotenv("config/secrets.env")

    # Initialize Flask App
    app = Flask(
        __name__,
        template_folder="web/templates",
        static_folder="web/static"
    )

    # Load Configuration
    config = get_config()
    app.config.from_object(config)

    # Setup Logging
    setup_logger(app)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(ivr_bp, url_prefix="/ivr")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(web_bp)

    # -----------------------------
    # Root Route (Fixes 404)
    # -----------------------------
    @app.route("/")
    def home():
        return redirect(url_for("web.login"))

    # -----------------------------
    # Health Check
    # -----------------------------
    @app.route("/health")
    def health():
        return {"status": "MedConnect running"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )
