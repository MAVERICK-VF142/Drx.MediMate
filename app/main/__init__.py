from flask import Blueprint

# Create the Blueprint instance for the 'main' part of the app
main_bp = Blueprint('main', __name__)
# Import routes to register them with the blueprint
from . import routes