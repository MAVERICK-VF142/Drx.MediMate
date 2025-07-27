from flask import Blueprint, request, jsonify
from ..utils.gemini_utils import (
    get_drug_information,
    get_symptom_recommendation,
    analyze_image_with_gemini,
    analyze_prescription_with_gemini,
    analyze_allergies
)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

api_bp = Blueprint('api', __name__)


# ---------------------------
# Common API Response Format
# ---------------------------
def api_response(message, status=200):
    return jsonify({'response': message}), status


# ---------------------------
# Gemini-Enhanced API Endpoints
# ---------------------------

@api_bp.route('/get_drug_info', methods=['POST'])
def get_drug_info():
    """
    Fetch information about a specific drug using Gemini.
    Request: { "drug_name": "Paracetamol" }
    """
    logging.info("💊 API /get_drug_info called")
    try:
        data = request.get_json()
        logging.info(f"📨 Request JSON: {data}")
        drug_name = data.get('drug_name')
        if not drug_name:
            logging.warning("❌ No drug name provided in request")
            return api_response('❌ No drug name provided.', 400)

        logging.info(f"🔍 Fetching drug info for: {drug_name}")
        response = get_drug_information(drug_name)
        return api_response(response)
    except Exception as e:
        logging.error(f"❌ Exception in /get_drug_info: {str(e)}")
        return api_response(f"❌ Error: {str(e)}", 500)


@api_bp.route('/symptom_checker', methods=['POST'])
def symptom_check():
    """
    Analyze symptoms and return possible conditions using Gemini.
    Request: { "symptoms": "fever, cough" }
    """
    logging.info("🤒 API /symptom_checker called")
    try:
        data = request.get_json()
        logging.info(f"📨 Request JSON: {data}")
        symptoms = data.get('symptoms')
        if not symptoms:
            logging.warning("❌ No symptoms provided.")
            return api_response('❌ No symptoms provided.', 400)

        logging.info(f"🧠 Analyzing symptoms: {symptoms}")
        result = get_symptom_recommendation(symptoms)
        return api_response(result)
    except Exception as e:
        logging.error(f"❌ Exception in /symptom_checker: {str(e)}")
        return api_response(f'❌ Error during analysis: {str(e)}', 500)


@api_bp.route('/process-upload', methods=['POST'])
def process_upload():
    """
    Analyze a base64 image captured from camera using Gemini Vision.
    Request: { "image_data": "<base64 string>" }
    """
    logging.info("📷 API /process-upload called")
    image_data = request.form.get("image_data")
    if not image_data:
        logging.warning("❌ No image received from camera.")
        return api_response('❌ No image received from camera.', 400)

    logging.info("🖼️ Image data received for Gemini analysis.")
    result = analyze_image_with_gemini(image_data)
    return api_response(result)


@api_bp.route('/validate-prescription', methods=['POST'])
def validate_prescription():
    """
    Analyze a prescription image using Gemini Vision.
    Request: { "image_data": "<base64 string>" }
    """
    logging.info("📩 API /validate-prescription called")
    image_data = request.form.get("image_data")
    if not image_data:
        logging.warning("❌ No image received for validation.")
        return api_response('❌ No image received for validation.', 400)

    logging.info("🧾 Prescription image received. Running validation.")
    result = analyze_prescription_with_gemini(image_data)
    logging.info(f"✅ Gemini result: {result}")
    return api_response(result)


@api_bp.route('/allergy_checker', methods=['POST'])
def allergy_checker():
    """
    Check for potential allergy conflicts with medicines using Gemini.
    Request: { "allergies": "penicillin", "medicines": "amoxicillin" }
    """
    logging.info("⚠️ API /allergy_checker called")
    try:
        data = request.get_json()
        logging.info(f"📨 Request JSON: {data}")
        allergies = data.get('allergies', '')
        medicines = data.get('medicines', '')

        if not allergies:
            logging.warning("❌ No allergies provided.")
            return api_response('❌ No allergies provided.', 400)
        if not medicines:
            logging.warning("❌ No medicines provided.")
            return api_response('❌ No medicines provided.', 400)

        logging.info("🔬 Running allergy-medicine interaction analysis...")
        result = analyze_allergies(allergies, medicines)
        return api_response(result)

    except Exception as e:
        logging.error(f"❌ Exception in /allergy_checker: {str(e)}")
        return api_response(f'❌ Error during allergy checking: {str(e)}', 500)
