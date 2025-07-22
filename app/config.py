import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-default-key-please-change-in-production'
    GEMINI_KEY = os.environ.get("GEMINI_KEY")
    FLASK_DEBUG = (os.getenv("FLASK_DEBUG", "false").lower() == "true") # For Flask debug mode

    if not GEMINI_KEY:
        # In a production environment, you might want to raise an error
        # or log a warning. For development, a default or warning is fine.
        print("❌ WARNING: GEMINI_KEY environment variable not set. AI features may not work.")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

# A dictionary to easily select configuration based on FLASK_ENV
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # Default to development if FLASK_ENV is not set
}