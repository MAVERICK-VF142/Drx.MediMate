from backend import create_app

app = create_app()

if __name__ == '__main__':
    import os
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Optional: Load environment variables from a .env file
    # from dotenv import load_dotenv
    # load_dotenv()

    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
