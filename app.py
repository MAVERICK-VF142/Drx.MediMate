import os
import json
import base64
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import markdown
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import pytesseract
import re
import uuid
import pdfkit
from dotenv import load_dotenv
load_dotenv()

# ---------------------------
# Configuration & Setup
# ---------------------------

# Load Gemini API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

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

    response = model.generate_content(prompt)
    text = response.text.strip() if response and hasattr(response, 'text') else "❌ No response from AI."
    return format_markdown_response(text)

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

    response = model.generate_content(prompt)
    text = response.text.strip() if response and hasattr(response, 'text') else "❌ No response from AI."
    return format_markdown_response(text)

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


        response = model.generate_content([prompt, image])
        text = response.text.strip() if response and hasattr(response, 'text') else "❌ Analysis failed or empty response from AI."
        return format_markdown_response(text)

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

def extract_prescription_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return {"error": "Invalid image format uploaded."}

        logging.info("Processing prescription image...")
        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "You're analyzing a medical prescription image. "
            "Extract the following in **structured JSON** format:\n\n"
            "```json\n"
            "{\n"
            "  \"medicines\": [\n"
            "    {\n"
            "      \"name\": \"\",\n"
            "      \"dose\": \"\",\n"
            "      \"frequency\": \"\",\n"
            "      \"duration\": \"\"\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "If fields are missing or illegible, leave them blank. Focus only on medicines prescribed. "
            "Ignore doctor's name or patient details unless relevant."
        )

        response = model.generate_content([prompt, image])
        text = response.text.strip()

        # Try extracting the JSON block from the markdown output
        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            extracted_json = json.loads(json_match.group(1))
            return extracted_json
        else:
            return {"error": "Failed to parse structured data from Gemini's response.", "raw_response": text}

    except Exception as e:
        logging.error(f"Gemini prescription analysis failed: {e}")
        return {"error": "Something went wrong during image analysis."}


def suggest_substitutes_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format.")
            return {"error": "Invalid image format uploaded."}

        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "You're analyzing a medicine package image to suggest brand substitutes.\n\n"
            "First, extract the **brand name** and identify the **active ingredient(s)**.\n"
            "Then, suggest 3–5 **other brands** (available in India or globally) with the same composition.\n\n"
            "Return the output in structured JSON like this:\n"
            "```json\n"
            "{\n"
            "  \"original_brand\": \"\",\n"
            "  \"active_ingredient\": \"\",\n"
            "  \"substitutes\": [\"\", \"\", \"\"]\n"
            "}\n"
            "```\n\n"
            "If the image is blurry or medicine cannot be identified, return:\n"
            "`{\"error\": \"Unable to identify medicine.\"}`"
        )

        response = model.generate_content([prompt, image])
        text = response.text.strip()

        json_match = re.search(r"\{[\s\S]+\}", text)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not parse Gemini response.", "raw_response": text}
    except Exception as e:
        logging.error(f"Gemini substitution suggestion failed: {e}")
        return {"error": "Substitution analysis failed."}


# ---------------------------
# Routes (Pages)
# ---------------------------

@app.route('/')
def sisu():
    return render_template('sisu.html')

@app.route('/doctor-dashboard')
def doctor():
    return render_template('doctor.html')

@app.route('/student-dashboard')
def student():
    return render_template('student.html')

@app.route('/pharmacist-dashboard')
def pharmacist():
    return render_template('pharmacist.html')

@app.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

@app.route('/upload_prescription', methods=['GET'])
def show_upload_prescription_page():
    return render_template('upload_prescription.html')

@app.route('/upload_prescription', methods=['POST'])
def upload_prescription():
    file = request.files.get('file')
    if not file:
        return render_template('upload_prescription.html', error="No file uploaded")

    # Read image content into memory
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{image_base64}"

    try:
        result = extract_prescription_with_gemini(image_data_url)
    except Exception as e:
        print(e)
        return render_template('upload_prescription.html', error=e)

    return render_template('upload_prescription.html', result=result, image_data=image_data_url)

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

@app.route('/my-account')
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })

@app.route('/suggest_substitute', methods=['GET'])
def show_suggest_substitute():
    return render_template('suggest_substitute.html')

@app.route('/suggest_substitute', methods=['POST'])
def suggest_substitute():
    file = request.files.get('file')
    if not file:
        return render_template('suggest_substitute.html', error="No file uploaded")

    try:
        # Read the uploaded image into memory
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        # Pass base64 image to Gemini
        result = suggest_substitutes_with_gemini(image_data_url)

        return render_template("suggest_substitute.html", result=result, image_data=image_data_url)

    except Exception as e:
        return render_template("suggest_substitute.html", error="Error during analysis")
    

@app.route('/clinical_support', methods=['GET', 'POST'])
def clinical_support():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        if not symptoms:
            return render_template('clinical_support.html', error="Please enter symptoms.")
        
        try:
            diagnosis = get_possible_diagnosis_with_gemini(symptoms)
            return render_template('clinical_support.html', symptoms=symptoms, diagnosis=diagnosis)
        except Exception as e:
            return render_template('clinical_support.html', error="Error in diagnosis generation.")
    
    return render_template('clinical_support.html')


def get_possible_diagnosis_with_gemini(symptoms_text):
    prompt = f"""A patient presents with the following symptoms: {symptoms_text}.
    Based on standard clinical knowledge, suggest possible diagnoses."""
    return call_gemini(prompt)


# Smart Prescription Generator
@app.route('/smart_prescription', methods=['GET', 'POST'])
def smart_prescription():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        if not symptoms:
            return render_template('smart_prescription.html', error="Please enter symptoms.")
        
        try:
            prescription_html = get_prescription_from_symptoms(symptoms)
            return render_template('smart_prescription.html', symptoms=symptoms, prescription_html=prescription_html)
        except Exception as e:
            print(e)
            return render_template('smart_prescription.html', error="Error in prescription generation.")
    
    return render_template('smart_prescription.html')


@app.route('/download_prescription', methods=['POST'])
def download_prescription():
    prescription_html = request.form.get('prescription_html')
    if not prescription_html:
        return "No content to download.", 400

    pdf = pdfkit.from_string(prescription_html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=prescription.pdf'
    return response


def get_prescription_from_symptoms(symptoms_text):
    prompt = f"""A patient reports the following symptoms: {symptoms_text}.
    Suggest a smart prescription including:
    - Drug Name
    - Dosage (in mg or ml)
    - Frequency (e.g., twice a day)
    - Duration (in days)
    
    Respond in pure HTML table format without explanation or extra text."""
    return call_gemini(prompt)


def call_gemini(prompt):

    response = model.generate_content(prompt)

    # Extract generated HTML (Gemini should return a table directly)
    if response and response.text:
        return response.text
    else:
        return "<p>Unable to generate prescription. Please try again.</p>"


@app.route('/get-health-tips')
def health_tips_page():
    return render_template("health_tips.html")

@app.route('/pharma-quiz')
def pharma_quiz_page():
    return render_template("pharma_quiz.html")

@app.route('/drug-news')
def drug_news_page():
    return render_template("drug_news.html")

@app.route('/get-health-tips', methods=['POST'])
def get_health_tips():
    data = request.json
    input_text = data.get("symptoms", "")
    prompt = f"Give 4 concise daily health tips based on a person's current health feeling: {input_text}"
    response = model.generate_content(prompt)
    return jsonify({"tips": response.text.strip()})

@app.route('/pharma-quiz', methods=['POST'])
def get_pharma_quiz():
    topic = request.json.get("topic", "")
    prompt = f"Explain the topic '{topic}' briefly (3-4 lines) and create a 10-mark multiple choice quiz with answers."
    response = model.generate_content(prompt)
    return jsonify({"quiz": response.text.strip()})

@app.route('/drug-news', methods=['GET'])
def get_drug_news():
    prompt = "Give a card-style list of the 3 latest news items related to pharmaceuticals: include title + 1-line summary."
    response = model.generate_content(prompt)
    return jsonify({"news": response.text.strip()})

# ---------------------------
# Run app
# ---------------------------

if __name__ == '__main__':

    logging.info("Starting Flask server...")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")

