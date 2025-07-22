# Drx.MediMate/app/symptom_checker/routes.py

from flask import render_template, request, current_app
from . import symptom_checker_bp
from .services import get_symptom_recommendation
from app.utils.helpers import api_response # <--- Import api_response here

@symptom_checker_bp.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('main/symptom_checker.html') 

@symptom_checker_bp.route('/symptom_checker', methods=['POST'])
def symptom_check():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms')
        if not symptoms:
            return api_response('❌ No symptoms provided.', 400) # <--- Use api_response
        
        result = get_symptom_recommendation(symptoms, current_app.gemini_model)
        return api_response(result) # <--- Use api_response
    except Exception as e:
        return api_response(f'❌ Error during analysis: {str(e)}', 500) # <--- Use api_response