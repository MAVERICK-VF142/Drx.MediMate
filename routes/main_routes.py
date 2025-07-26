import json
import base64
import logging
from flask import Blueprint, render_template, request, jsonify
from PIL import Image
from io import BytesIO

from services.ai_service import (
    get_drug_information,
    get_symptom_recommendation,
    analyze_image_with_gemini,
    LANGUAGE_CODES, 
    INDIAN_LANGUAGES 
)

main_bp = Blueprint('main', __name__)

# ---------------------------
# Utility
# ---------------------------

def api_response(message, status=200):
    """Standard JSON response helper"""
    return jsonify({'response': message}), status

# ---------------------------
# Routes (Pages)
# ---------------------------

@main_bp.route('/')
def sisu():
    return render_template('sisu.html')

@main_bp.route('/index.html')
def index():
    return render_template('index.html')

@main_bp.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html', INDIAN_LANGUAGES=INDIAN_LANGUAGES)

@main_bp.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html', INDIAN_LANGUAGES=INDIAN_LANGUAGES)

@main_bp.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

@main_bp.route('/my-account')
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })

# ---------------------------
# API Endpoints (AJAX/JS)
# ---------------------------

@main_bp.route('/get_drug_info', methods=['POST'])
def get_drug_info_api():
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

@main_bp.route('/symptom_checker', methods=['POST'])
def symptom_check_api():
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

@main_bp.route('/translate', methods=['POST'])
def translate_text_api():
    data = request.get_json()
    text = data.get('text', '')
    lang_name = data.get('language', '') 

    if not text or not lang_name:
        return jsonify({'response': 'Invalid input'}), 400

    target_lang_code = LANGUAGE_CODES.get(lang_name)

    if not target_lang_code:
        logging.warning(f"❌ Invalid or unsupported target language name: {lang_name}")
        return jsonify({'response': 'Unsupported language for translation'}), 400

    try:
        from deep_translator import GoogleTranslator 
        translated = GoogleTranslator(target=target_lang_code).translate(text)
        return jsonify({'response': translated})
    except Exception as e:
        logging.error(f"Translation error: {e}") 
        return jsonify({'response': 'Translation failed'}), 500

@main_bp.route('/process-upload', methods=['POST'])
def process_upload_api():
    logging.info("API /process-upload called")
    image_data = request.form.get("image_data")
    if image_data:
        logging.info("Image data received for analysis")
        result = analyze_image_with_gemini(image_data)
        return render_template("upload_image.html", result=result)
    else:
        logging.warning("❌ No image data received in request")
    return render_template("upload_image.html", result="❌ No image data received.")
