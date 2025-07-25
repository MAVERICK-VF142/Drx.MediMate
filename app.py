import os
from dotenv import load_dotenv
load_dotenv()  
import json
import base64
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from io import BytesIO
import google.generativeai as genai
import markdown
import logging
import time

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

# ---------------------------
# Configuration & Setup
# ---------------------------

# Load Gemini API key from environment variable
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_KEY environment variable not set.")
genai.configure(api_key=api_key)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------
# Retry Helper Function
# ---------------------------

def gemini_generate_with_retry(prompt, max_retries=3, delay=2, timeout=20):
    """
    Calls Gemini API with timeout and retry logic.
    - Retries failed calls (with exponential backoff)
    - Aborts slow responses gracefully
    """
    attempt = 0
    while attempt < max_retries:
        try:
            logging.info(f"🌐 Gemini API Call Attempt {attempt + 1}")
            
            # Set up timeout using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                response = future.result(timeout=timeout)  # Timeout in seconds

            # Check if response is valid
            if response and hasattr(response, 'text') and response.text.strip():
                logging.info("✅ Gemini API call successful.")
                return response
            else:
                logging.warning("⚠️ Empty or malformed response. Retrying...")

        except FuturesTimeout:
            logging.error(f"⏰ Gemini API call timed out after {timeout} seconds.")
        except Exception as e:
            logging.error(f"❌ Gemini API error: {str(e)}")

        # Backoff delay before retry
        wait_time = delay * (2 ** attempt)  # 2s, 4s, 8s...
        logging.info(f"⏳ Waiting {wait_time}s before retry attempt {attempt + 2}")
        time.sleep(wait_time)
        attempt += 1
        
    logging.critical("❌ All Gemini API retry attempts failed.")
    return None

# ---------------------------
# Utility Functions
# ---------------------------

def api_response(message, status=200):
    """Standard JSON response helper"""
    return jsonify({'response': message}), status

def format_markdown_response(text):
    """Convert Markdown text to HTML for consistent, readable output"""
    if not text or text.startswith("❌"):
        return text  # Return error messages as-is
    # Convert Markdown to HTML
    html = markdown.markdown(text, extensions=['extra', 'fenced_code'])
    # Wrap in a styled div for better presentation
    return f'<div class="markdown-content">{html}</div>'

# ---------------------------
# AI Functions
# ---------------------------

def get_drug_information(drug_name):
    prompt = (
        f"Provide a brief clinical summary for pharmacists on the drug **{drug_name}** in Markdown format:\n"
        "## Therapeutic Uses\n"
        "- List primary therapeutic uses\n"
        "## Standard Dosage\n"
        "- Provide standard adult dosage (include administration route and frequency)\n"
        "## Common Side Effects\n"
        "- List common side effects\n"
        "## Serious Side Effects\n"
        "- List serious side effects requiring immediate attention\n"
        "## Contraindications\n"
        "- List conditions or scenarios where the drug should not be used\n"
        "## Important Drug Interactions\n"
        "- List significant drug interactions\n"
        "Use concise bullet points. Ensure clarity and professional tone."
    )

    logging.info(f"Prompt to Gemini: {prompt}")

    cached = get_cached_drug(drug_name)
    if cached:
        logging.info(f"📦 Cache hit for drug: {drug_name}")
        return cached

    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            formatted = format_markdown_response(text)
            set_cached_drug(drug_name, formatted)
            logging.info("✅ Cached new drug info response.")
            return formatted
        else:
            logging.warning("No text in AI response.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"Exception in get_drug_information: {str(e)}")
        return f"❌ Error: {str(e)}"
    
def predict_disease(symptoms):
    prompt = (
        f"""
            You are a medical assistant powered by the latest knowledge as of October 2023.

            Given the following symptoms: **{symptoms}**, perform a comprehensive analysis to predict the most likely diseases or conditions.

            ### Possible Diseases
            - List the top 3–5 potential diseases or conditions that match the **combined symptom profile**.
            - Prioritize common, serious, and high-likelihood conditions.

            ###  Description
            - For each predicted disease, provide a 1–2 sentence explanation of how the listed symptoms relate to it.

            ### Symptom-wise Breakdown
            For each symptom, provide:
                - **Symptom:** [Symptom name]  
                - **Possible Disease:** [Likely associated disease]  
                - **Explanation:** [Brief explanation of the relationship between the symptom and the disease]

            ### When to Seek Immediate Medical Attention
                - Highlight any listed symptoms or symptom combinations that may indicate a medical emergency.
                - Use clear, layman-friendly language to help the user understand urgency.

            **Instructions:**  
                - Use Markdown formatting.  
                - Avoid general disclaimers (e.g., "consult a doctor").  
                - Ensure clinical relevance and clarity.  
                - Do not repeat the same disease unless strongly justified.
        """

    )
    logging.info(f"Prompt to Gemini for disease prediction: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("✅ Received response from Gemini for disease prediction.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No text in AI response for disease prediction.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in predict_disease: {str(e)}")
        return f"❌ Error: {str(e)}"

def get_symptom_recommendation(symptoms):
    prompt = (
        f"Given the symptoms: **{symptoms}**, recommend over-the-counter treatment options in Markdown format:\n"
        "## Recommended Over-the-Counter Treatments\n"
        "- List appropriate OTC medications or treatments\n"
        "## Common Side Effects\n"
        "- List common side effects of recommended treatments\n"
        "## Important Interactions\n"
        "- List significant drug or condition interactions\n"
        "## Safety Tips\n"
        "- Provide key safety tips or precautions\n"
        "If symptoms suggest a medical emergency or severe condition, clearly state: **'Seek immediate medical attention.'** "
        "Use concise bullet points in Markdown format. Avoid disclaimers."
    )

    logging.info(f"Prompt to Gemini for symptom check: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("Received response from Gemini for symptoms.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No text in AI response for symptoms.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in get_symptom_recommendation: {str(e)}")
        return f"❌ Error: {str(e)}"

def analyze_image_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return "❌ Invalid image format uploaded."

        logging.info("Decoding and processing image for AI analysis...")
        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "Analyze this image of a medicine or drug packaging. Provide the response in Markdown format:\n"
            "## Drug Information\n"
            "- **Drug Name**: Identify the drug name (if visible)\n"
            "- **Manufacturer**: Identify the manufacturer (if visible)\n"
            "## Clinical Summary\n"
            "- **Therapeutic Uses**: List primary uses\n"
            "- **Standard Dosage**: Provide standard dosage\n"
            "- **Common Side Effects**: List common side effects\n"
            "- **Serious Side Effects**: List serious side effects\n"
            "- **Contraindications**: List contraindications\n"
            "- **Important Interactions**: List significant interactions\n"
            "If the image is blurry or unclear, respond with: **'Please retake the image for better clarity.'**"
        )

        logging.info("Sending prompt and image to Gemini AI.")
        response = gemini_generate_with_retry([prompt, image])
        
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("AI analysis complete.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ Analysis failed or empty AI response.")
            return "❌ Analysis failed or empty response from AI."

    except Exception as e:
        logging.error(f"❌ Error during image analysis: {str(e)}")
        return f"❌ Error during image analysis: {str(e)}"

def analyze_prescription_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return "❌ Invalid image format uploaded."

        logging.info("Decoding and processing prescription image for validation...")
        
         # Clean base64 string
        if "," in image_data:
            image_data = image_data.split(",")[1]

        # Decode base64 to binary
        image_bytes = base64.b64decode(image_data)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes)) 

        prompt = (
            "You are a medical assistant AI.\n"
            "Given an image of a **prescription**, extract and analyze:\n\n"
            "### Step 1: Extract Prescription Details\n"
            "- List all **medications/drugs** mentioned.\n"
            "- Include **dosage**, **frequency**, and **duration** if visible.\n\n"
            "### Step 2: Validation\n"
            "- Check for **duplicate drugs** or overlapping medicines.\n"
            "- Check for **drug-drug interactions**.\n"
            "- Flag any **potentially harmful combinations**.\n"
            "- If dosage looks too high or low, **flag it**.\n\n"
            "### Output Format (Markdown)\n"
            "## Extracted Prescription\n"
            "- Drug 1: [Name], [Dosage], [Frequency], [Duration]\n"
            "- ...\n\n"
            "## AI-Powered Feedback\n"
            "- Safety Warnings:\n"
            "- Interaction Notes:\n"
            "- Suggestions:\n\n"
            "If the image is unclear or handwriting is illegible, reply with:\n"
            "**'⚠️ The prescription image is too unclear to read. Please retake it in good lighting.'**"
        )

        logging.info("Sending prescription image to Gemini for validation...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        if response is not None:
            logging.info(f"Gemini Raw Response: {response}")
        else:
            logging.warning("⚠️ Gemini response is None.")

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("✅ Prescription validation complete.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No response or empty output from Gemini.")
            return "❌ No useful output received from Gemini."

    except Exception as e:
        logging.error(f"❌ Error during prescription validation: {str(e)}")
        return f"❌ Error during prescription validation: {str(e)}"


# ---------------------------_
# Authentication & Dashboard Routes
# ---------------------------

@app.route('/')
def index_redirect():
    # Redirect to login page
    return render_template('sisu.html')

@app.route('/sisu.html')
def sisu():
    return render_template('sisu.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

# Alternative route for index
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# Role-specific Dashboard Routes
@app.route('/doctor-dashboard.html')
def doctor_dashboard():
    return render_template('doctor-dashboard.html')

@app.route('/pharmacist-dashboard.html')
def pharmacist_dashboard():
    return render_template('pharmacist-dashboard.html')

@app.route('/student-dashboard.html')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/patient-dashboard.html')
def patient_dashboard():
    return render_template('patient-dashboard.html')


# ---------------------------
# Feature Page Routes
# ---------------------------

@app.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

@app.route('/prescription-validator-page')
def prescription_validator_page():
    return render_template('prescription_validator.html')

@app.route('/my-account')
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })

# Additional feature routes that may be referenced in the dashboard
@app.route('/inventory-management')
def inventory_management():
    return render_template('inventory_management.html')

@app.route('/prescription-processing')
def prescription_processing():
    return render_template('prescription_processing.html')

@app.route('/patient-records')
def patient_records():
    return render_template('patient_records.html')

@app.route('/educational-resources')
def educational_resources():
    return render_template('educational_resources.html')

@app.route('/medication-tracker')
def medication_tracker():
    return render_template('medication_tracker.html')

# ---------------------------
# API Endpoints (AJAX/JS)
# ---------------------------

@app.route('/get_drug_info', methods=['POST'])
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

@app.route('/symptom_checker', methods=['POST'])
def symptom_check():
    logging.info("API /symptom_checker called")
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        symptoms = data.get('symptoms')
        action = data.get('action', 'analyze')
        if not symptoms:
            logging.warning("❌ No symptoms provided.")
            return api_response('❌ No symptoms provided.', 400)
        if action == 'predict':
            logging.info(f"Calling predict_disease with symptoms: {symptoms}")
            result = predict_disease(symptoms)
        else:
            logging.info(f"Calling get_symptom_recommendation with symptoms: {symptoms}")
            result = get_symptom_recommendation(symptoms)

        return api_response(result)
    except Exception as e:
        logging.error(f"❌ Exception in /symptom_checker: {str(e)}")
        return api_response(f'❌ Error during analysis: {str(e)}', 500)

@app.route('/process-upload', methods=['POST'])
def process_upload():
    logging.info("API /process-upload called")
    image_data = request.form.get("image_data")
    if image_data:
        logging.info("Image data received for analysis")
        result = analyze_image_with_gemini(image_data)
        print(result)
        return jsonify({'result': result})
    else:
        logging.warning("❌ No image data received in request")
    return jsonify({'result': '❌ No image received from camera.'})


@app.route('/validate-prescription', methods=['POST'])
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


# ---------------------------
# Error Handlers
# ---------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ---------------------------
# Run App
# ---------------------------

if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")