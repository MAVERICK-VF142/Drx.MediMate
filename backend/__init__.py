from flask import Flask
from flask_cors import CORS
import os
import google.generativeai as genai



def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load API key
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        raise EnvironmentError("❌ GEMINI_KEY not set.")
    genai.configure(api_key=api_key)

   
    # Blueprint imports
    from .routes.auth_routes import auth_bp
    from .routes.dashboard_routes import dashboard_bp
    from .routes.feature_routes import feature_bp
    from .routes.api_routes import api_bp
    from .routes.error_handlers import errors_bp
    from .routes.admin_routes import admin_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(feature_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(admin_bp)

    return app
