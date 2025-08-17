################ blueprint not registered ----------- this file and these routes are redundent , all thing are implemented in api_routes , so will remove it later after careful inspection
from flask import Blueprint, render_template, request, jsonify
from backend.utils.gemini_utils import (
    get_drug_information,
    get_symptom_recommendation,
    analyze_image_with_gemini,
    drug_side_effect_checker,
    analyze_prescription_with_gemini
)



ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ask", methods=["POST"])
def ask_gemini():
    data = request.json
    question_type = data.get("type")

    if question_type == "drug":
        response = get_drug_information(data.get("query", ""))
    elif question_type == "symptom":
        response = get_symptom_recommendation(data.get("query", ""))
    else:
        response = "Unknown query type."

    return jsonify({"response": response})





# @ai_bp.route("/predict_side_effects", methods=["POST"])
# def predict_side_effects():
#     data = request.json
#     drug_name = data.get("drug_name")
#     if not drug_name:
#         return jsonify({"error": "Drug name required"}), 400
#     try:
#         result = drug_side_effect_checker(drug_name)
#         return jsonify({"response": result})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    

@ai_bp.route("/upload-image", methods=["POST"])
def upload_image():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "No image uploaded"}), 400

    image_bytes = image.read()
    try:
        result = analyze_image_with_gemini(image_bytes)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




        