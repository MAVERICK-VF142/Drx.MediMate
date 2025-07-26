import os

class Config:
    """
    Application configuration settings.
    Loads sensitive information from environment variables.
    """
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key_that_should_be_changed")
    GEMINI_KEY = os.getenv("GEMINI_KEY")

    if not GEMINI_KEY:
        raise EnvironmentError("❌ GEMINI_KEY environment variable not set in .env or environment.")

