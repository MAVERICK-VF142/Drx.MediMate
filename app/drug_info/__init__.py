from flask import Blueprint

# Create the Blueprint instance for the 'drug_info' part
drug_info_bp = Blueprint('drug_info', __name__)

# Import routes to register them with the blueprint
from . import routes
