from flask import Blueprint
image_processing_bp = Blueprint('image_processing', __name__)
from . import routes