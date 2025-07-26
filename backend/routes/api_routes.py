from flask import Blueprint, request, jsonify
from ..utils.gemini_utils import get_drug_information, get_symptom_recommendation, analyze_image_with_gemini, analyze_prescription_with_gemini

import logging
logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")


api_bp = Blueprint('api', __name__)


# ---------------------------
# API Endpoints (AJAX/JS)
# ---------------------------

def api_response(message, status=200):
    return jsonify({'response': message}), status



@api_bp.route('/get_drug_info', methods=['POST'])
def get_drug_info():
    logging.info("API /get_drug_info called")
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        drug_name = data.get('drug_name')
        if not drug_name:
            logging.warning("No drug name provided in request")
            return api_response('❌ No drug name provided.', 400)
        logging.info(f"Calling get_drug_information with drug_name: {drug_name}")
        response = get_drug_information(drug_name)
        return api_response(response)
    except Exception as e:
        logging.error(f"Exception in /get_drug_info: {str(e)}")
        return api_response(f"❌ Error: {str(e)}", 500)



@api_bp.route('/symptom_checker', methods=['POST'])
def symptom_check():
    logging.info("API /symptom_checker called")
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        symptoms = data.get('symptoms')
        if not symptoms:
            logging.warning("❌ No symptoms provided.")
            return api_response('❌ No symptoms provided.', 400)
        logging.info(f"Calling get_symptom_recommendation with symptoms: {symptoms}")
        result = get_symptom_recommendation(symptoms)
        return api_response(result)
    except Exception as e:
        logging.error(f"❌ Exception in /symptom_checker: {str(e)}")
        return api_response(f'❌ Error during analysis: {str(e)}', 500)

@api_bp.route('/process-upload', methods=['POST'])
def process_upload():
    logging.info("API /process-upload called")
    image_data = request.form.get("image_data")
    if image_data:
        logging.info("Image data received for analysis")
        result = analyze_image_with_gemini(image_data)
        return jsonify({'result': result})
    else:
        logging.warning("❌ No image data received in request")
    return jsonify({'result': '❌ No image received from camera.'})

@api_bp.route('/validate-prescription', methods=['POST'])
def validate_prescription():
    logging.info("📩 API /validate-prescription called")

    image_data = request.form.get("image_data")
    if image_data:
        logging.info("📷 Prescription image data received for validation")

        # Process the image with Gemini (replace with your validator logic)
        result = analyze_prescription_with_gemini(image_data)

        logging.info(f"✅ Gemini result: {result}")
        return jsonify({'result': result})
    else:
        logging.warning("❌ No image data received in /validate-prescription")
        return jsonify({'result': '❌ No image received for validation.'})
