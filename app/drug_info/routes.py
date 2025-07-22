from flask import render_template, request, jsonify, current_app
from . import drug_info_bp # Import the blueprint instance
from .services import get_drug_information # Will create this next
from app.utils.helpers import api_response 

@drug_info_bp.route('/drug-info-page')
def drug_info_page():
    return render_template('drugs/drug_info.html') # Update template path

@drug_info_bp.route('/get_drug_info', methods=['POST'])
def get_drug_info():
    try:
        data = request.get_json()
        drug_name = data.get('drug_name')
        if not drug_name:
            return api_response('❌ No drug name provided.', 400) # <--- Use api_response

        response_text = get_drug_information(drug_name, current_app.gemini_model)
        return api_response(response_text) # <--- Use api_response
    except Exception as e:
        return api_response(f"❌ Error: {str(e)}", 500) # <--- Use api_response