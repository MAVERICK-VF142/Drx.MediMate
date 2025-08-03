from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load environment variables
    load_dotenv()

    # MongoDB + Secret Key setup
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/healthmate")
    app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

    # Initialize Mongo
    mongo.init_app(app)
    app.mongo = mongo

    # Register blueprints
    with app.app_context():
        from .routes.auth_routes import auth_bp
        from .routes.dashboard_routes import dashboard_bp
        from .routes.feature_routes import feature_bp
        from .routes.api_routes import api_bp
        from .routes.error_handlers import error_bp
        from .routes.admin_routes import admin_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(feature_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(error_bp)
        app.register_blueprint(admin_bp)

    return app