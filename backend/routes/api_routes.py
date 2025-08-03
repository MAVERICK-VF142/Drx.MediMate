from flask import Blueprint, request, jsonify, current_app
from ..utils.gemini_utils import (
    get_drug_information,
    get_symptom_recommendation,
    analyze_image_with_gemini,
    analyze_prescription_with_gemini,
    analyze_allergies
)
from ..models.health_data_model import get_health_data, add_health_data
from backend.utils.jwt_utils import token_required  

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

api_bp = Blueprint('api', __name__)


# ---------------------------
# API Endpoints (AJAX/JS)
# ---------------------------

def api_response(message, status=200):
    return jsonify({'response': message}), status


# 🔓 Public Route
@api_bp.route('/get_drug_info', methods=['POST'])
def get_drug_info():
    logging.info("API /get_drug_info called")
    try:
        data = request.get_json()
        drug_name = data.get('drug_name')
        if not drug_name:
            return api_response('❌ No drug name provided.', 400)
        response = get_drug_information(drug_name)
        return api_response(response)
    except Exception as e:
        return api_response(f"❌ Error: {str(e)}", 500)


# 🔐 Protected Route
@api_bp.route('/symptom_checker', methods=['POST'])
@token_required  
def symptom_check(current_user):
    logging.info(f"API /symptom_checker called by: {current_user}")
    try:
        data = request.get_json()
        symptoms = data.get('symptoms')
        if not symptoms:
            return api_response('❌ No symptoms provided.', 400)
        result = get_symptom_recommendation(symptoms)
        return api_response(result)
    except Exception as e:
        return api_response(f'❌ Error during analysis: {str(e)}', 500)


# 🔐 Protected Route
@api_bp.route('/process-upload', methods=['POST'])
@token_required
def process_upload(current_user):
    logging.info(f"API /process-upload called by: {current_user}")
    image_data = request.form.get("image_data")
    if image_data:
        result = analyze_image_with_gemini(image_data)
        return jsonify({'result': result})
    return jsonify({'result': '❌ No image received from camera.'})


# 🔐 Protected Route
@api_bp.route('/validate-prescription', methods=['POST'])
@token_required
def validate_prescription(current_user):
    logging.info(f"📩 API /validate-prescription called by: {current_user}")
    image_data = request.form.get("image_data")
    if image_data:
        result = analyze_prescription_with_gemini(image_data)
        return jsonify({'result': result})
    return jsonify({'result': '❌ No image received for validation.'})


# 🔐 Protected Route
@api_bp.route('/allergy_checker', methods=['POST'])
@token_required
def allergy_checker(current_user):
    logging.info(f"📩 API /allergy_checker called by: {current_user}")
    try:
        data = request.get_json()
        allergies = data.get('allergies', '')
        medicines = data.get('medicines', '')
        if not allergies:
            return api_response('❌ No allergies provided.', 400)
        if not medicines:
            return api_response('❌ No Medicines provided.', 400)
        result = analyze_allergies(allergies, medicines)
        return api_response(result)
    except Exception as e:
        return api_response(f'❌ Error during allergy checking: {str(e)}', 500)


# 🔐 Protected GET Route
@api_bp.route('/api/health-data', methods=['GET'])
@token_required
def fetch_health_data(current_user):
    logging.info(f"API /api/health-data [GET] called by: {current_user}")
    try:
        data = get_health_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🔐 Protected POST Route
@api_bp.route('/api/health-data', methods=['POST'])
@token_required
def create_health_data(current_user):
    logging.info(f"API /api/health-data [POST] called by: {current_user}")
    try:
        payload = request.get_json()
        add_health_data(payload)
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
