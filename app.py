import os
import json
import base64
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from flask import session

INDIAN_LANGUAGES = [
    "English", "Assamese", "Bengali", "Bodo", "Dogri", "Gujarati", "Hindi", "Kannada",
    "Kashmiri", "Konkani", "Maithili", "Malayalam", "Manipuri", "Marathi", "Nepali", 
    "Odia", "Punjabi", "Sanskrit", "Santali", "Sindhi", "Tamil", "Telugu", "Urdu"
]


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

# Retry Helper Function
# gemini_generate_with_retry() supports both string and list prompts
def gemini_generate_with_retry(prompt, max_retries=3, delay=2, timeout=10):
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
# Utility
# ---------------------------

def api_response(message, status=200):
    """Standard JSON response helper"""
    return jsonify({'response': message}), status

# ---------------------------
# AI Functions
# ---------------------------

def get_drug_information(drug_name):
    prompt = (
        f"Provide a brief clinical summary for pharmacists on the drug {drug_name}:\n"
        "- Therapeutic uses\n"
        "- Standard dosage\n"
        "- Common & serious side effects\n"
        "- Contraindications\n"
        "- Important drug interactions\n"
        "Answer concisely in bullet points suitable for quick reference."
    )
    logging.info(f"Prompt to Gemini: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        logging.info("Received response from Gemini AI.")
        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            logging.warning("No text in AI response.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"Exception in get_drug_information: {str(e)}")
        return f"❌ Error: {str(e)}"

def get_symptom_recommendation(symptoms):
    prompt = (
        f"Given the symptoms: {symptoms}, recommend over-the-counter treatment options."
        " List common side effects, important interactions, and safety tips. "
        " If symptoms suggest a medical emergency or severe condition, recommend immediate doctor consultation. "
        "Respond concisely in bullet points without disclaimers."
    )
    logging.info(f"Prompt to Gemini for symptom check: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        logging.info("Received response from Gemini for symptoms.")
        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            logging.warning("❌ No text in AI response for symptoms.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in get_symptom_recommendation: {str(e)}")
        return f"❌ Error: {str(e)}"
        
def translate_output(text, target_language):
    prompt = f"Translate the following into {target_language}:\n\n{text}"
    response = gemini_generate_with_retry(prompt)
    if response and hasattr(response, 'text'):
        return response.text.strip()
    return "❌ Translation failed or no response."

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
            "Analyze this image of a medicine or drug packaging. "
            "Identify the drug name, manufacturer (if visible), and give a brief clinical summary. "
            "If the image is blurry or unclear, politely ask the user to retake it."
        )

        logging.info("Sending prompt and image to Gemini AI.")
        # gemini_generate_with_retry() supports both string and list prompts
        response = gemini_generate_with_retry([prompt, image])
        text = response.text.strip() if response and hasattr(response, 'text') else None
        if not text:
            logging.warning("❌ Analysis failed or empty AI response.")
            return "❌ Analysis failed or empty response from AI."
        
        logging.info("AI analysis complete.")
        return text

    except Exception as e:
        logging.error(f"❌ Error during image analysis: {str(e)}")
        return f"❌ Error during image analysis: {str(e)}"

# ---------------------------
# Routes (Pages)
# ---------------------------

@app.route('/')
def sisu():
    return render_template('sisu.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

@app.route('/show-translate')
def show_translate():
    if 'last_output' not in session:
        session['last_output'] = ''  # Initialize with a default value if not set
    result = session.get('last_output', '')  
    return render_template("translate.html", indian_languages=INDIAN_LANGUAGES, result=result)


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
        if not symptoms:
            logging.warning("❌ No symptoms provided.")
            return api_response('❌ No symptoms provided.', 400)
        logging.info(f"Calling get_symptom_recommendation with symptoms: {symptoms}")
        result = get_symptom_recommendation(symptoms)
        return api_response(result)
    except Exception as e:
        logging.error(f"❌ Exception in /symptom_checker: {str(e)}")
        return api_response(f'❌ Error during analysis: {str(e)}', 500)

@app.route('/translate', methods=['POST'])
def translate_text():
    logging.info("API /translate called")
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        text = data.get('text')
        language = data.get('language')
        if not text or not language:
            return api_response('❌ Text and language are required.', 400)
        
        translated = translate_output(text, language)
        return api_response(translated)
    except Exception as e:
        logging.error(f"❌ Error in /translate: {str(e)}")
        return api_response(f"❌ Translation failed: {str(e)}", 500)


@app.route('/process-upload', methods=['POST'])
def process_upload():
    logging.info("API /process-upload called")
    image_data = request.form.get("image_data")
    if image_data:
        logging.info("Image data received for analysis")
        result = analyze_image_with_gemini(image_data)
        return render_template("upload_image.html", result=result)
    else:
        logging.warning("❌ No image data received in request")
    return render_template("upload_image.html", result="❌ No image data received.")

###############################################
@app.route('/my-account')
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })
###############################################

# ---------------------------
# Run app
# ---------------------------

if __name__ == '__main__':
    # Use FLASK_DEBUG=true in your environment to enable debug mode
    logging.info("Starting Flask server...")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
