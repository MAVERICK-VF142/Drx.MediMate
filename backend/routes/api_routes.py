from flask import Blueprint, request, jsonify
from ..utils.gemini_utils import get_drug_information, get_symptom_recommendation, analyze_image_with_gemini, analyze_prescription_with_gemini, analyze_allergies, get_drug_comparison_summary
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

@api_bp.route('/compare_drugs_summary', methods=['POST'])
def compare_drugs_summary():
    logging.info("API /compare_drugs_summary called")
    try:
        data = request.get_json()
        drug1 = data.get('drug1')
        drug2 = data.get('drug2')

        if not drug1 or not drug2:
            return api_response("❌ Both drug names are required.", 400)

        summary = get_drug_comparison_summary(drug1, drug2)
        return jsonify({'summary': summary})

    except Exception as e:
        logging.exception("❌ Exception in /compare_drugs_summary")
        return api_response(f"❌ Internal error: {str(e)}", 500)

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


@api_bp.route('/allergy_checker', methods=['POST'])
def allergy_checker():
    """
    Endpoint to analyze allergies vs medicines using Gemini.
    """
    logging.info("📩 API allergy-checker called")

    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        allergies = data.get('allergies', '')
        medicines = data.get('medicines', '')

        if not allergies:
            logging.warning("❌ No allergies provided.")
            return api_response('❌ No allergies provided.', 400)
        if not medicines:
            logging.warning("❌ No Medicines provided.")
            return api_response('❌ No Medicines provided.', 400)

        result = analyze_allergies(allergies, medicines)
        return api_response(result)

    except Exception as e:
        logging.error(f"❌ Exception in /allergy_checker: {str(e)}")
        return api_response(f'❌ Error during allergy checking: {str(e)}', 500)


@api_bp.route('/compare_drugs', methods=['POST'])
def compare_drugs():
    """
    Endpoint to compare 2-3 drugs side by side using existing drug info API.
    """
    logging.info("📩 API /compare_drugs called")
    
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        
        drugs = data.get('drugs', [])
        
        if not drugs or len(drugs) < 2:
            logging.warning("❌ At least 2 drugs required for comparison.")
            return api_response('❌ At least 2 drugs are required for comparison.', 400)
        
        if len(drugs) > 3:
            logging.warning("❌ Maximum 3 drugs allowed for comparison.")
            return api_response('❌ Maximum 3 drugs allowed for comparison.', 400)
        
        # Get individual drug information for each drug
        drug_info_results = {}
        for drug in drugs:
            if not drug.strip():
                continue
            logging.info(f"Getting info for drug: {drug}")
            drug_info = get_drug_information(drug.strip())
            drug_info_results[drug.strip()] = drug_info
        
        if len(drug_info_results) < 2:
            logging.warning("❌ Could not retrieve information for at least 2 drugs.")
            return api_response('❌ Could not retrieve information for at least 2 drugs.', 400)
        
        # Return the comparison data
        return jsonify({
            'status': 'success',
            'drugs': list(drug_info_results.keys()),
            'comparison_data': drug_info_results
        })
        
    except Exception as e:
        logging.error(f"❌ Exception in /compare_drugs: {str(e)}")
        return api_response(f'❌ Error during drug comparison: {str(e)}', 500)

