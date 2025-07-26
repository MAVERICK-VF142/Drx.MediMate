import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv # Import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Import configuration
from config import Config

# Import blueprints
from routes.main_routes import main_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def create_app():
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load configuration from Config object
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing
    CORS(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    logging.info("Flask application initialized and blueprints registered.")
    return app

# If running directly, create and run the app
if __name__ == '__main__':
    app = create_app()
    # Use FLASK_DEBUG=true in your environment to enable debug mode
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
