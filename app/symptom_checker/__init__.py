# app/symptom_checker/__init__.py
from flask import Blueprint
symptom_checker_bp = Blueprint('symptom_checker', __name__)
from . import routes
