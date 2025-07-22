# Drx.MediMate/app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
import google.generativeai as genai
from .config import config_by_name

def create_app(config_name=None):
    static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder=static_folder_path
    )

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config_by_name[config_name])

    CORS(app)

    # Drx.MediMate/app/__init__.py (TEMPORARY MODIFICATION FOR DEVELOPMENT WITHOUT API KEY)
# ...
    gemini_api_key = app.config.get("GEMINI_KEY")

    # --- TEMPORARY: Handle missing GEMINI_KEY for structural testing ---
    if not gemini_api_key:
        print("❌ WARNING: GEMINI_KEY environment variable not set. AI features will be disabled or mocked.")
        # Assign a dummy model or a flag to indicate AI is not active
        app.gemini_model = None # Set to None, or a mock object
        # You might also want to set a flag in config to control AI features
        app.config['AI_ENABLED'] = False 
    else:
        genai.configure(api_key=gemini_api_key)
        app.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        app.config['AI_ENABLED'] = True
 
    # --- Register Blueprints ---
    from .main import main_bp
    app.register_blueprint(main_bp) # For /, index.html, sisu.html

    from .drug_info import drug_info_bp
    app.register_blueprint(drug_info_bp) # For drug-info-page and get_drug_info API

    from .symptom_checker import symptom_checker_bp
    app.register_blueprint(symptom_checker_bp) # For symptom-checker-page and symptom_checker API

    from .image_processing import image_processing_bp
    app.register_blueprint(image_processing_bp) # For upload-image-page and process-upload API
    # --- End Blueprint Registration ---

    return app