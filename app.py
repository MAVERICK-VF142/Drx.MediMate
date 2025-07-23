import os
import json
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import markdown
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from models import db, MedicineReminder
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------------------
# Configuration & Setup
# ---------------------------

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_KEY environment variable not set.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medimate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

with app.app_context():
    db.init_app(app)
    db.create_all()

reminders = []

scheduler = BackgroundScheduler()
@scheduler.scheduled_job('interval', minutes=1)
def check_reminders():
    now = datetime.now()
    for reminder in reminders:
        if not reminder['sent'] and now >= reminder['time']:
            try:
                msg = Message('Medicine Reminder 💊',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[reminder['email']])
                msg.body = f"Hello! Time to take your medicine: {reminder['med_name']}"
                mail.send(msg)
                reminder['sent'] = True
            except Exception as e:
                print(f"Error sending email: {e}")

scheduler.start()

# ---------------------------
# Retry Helper Function
# ---------------------------

def gemini_generate_with_retry(prompt, max_retries=3, delay=2, timeout=10):
    attempt = 0
    while attempt < max_retries:
        try:
            logging.info(f"🌐 Gemini API Call Attempt {attempt + 1}")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                response = future.result(timeout=timeout)
            if response and hasattr(response, 'text') and response.text.strip():
                logging.info("✅ Gemini API call successful.")
                return response
            else:
                logging.warning("⚠️ Empty or malformed response. Retrying...")
        except FuturesTimeout:
            logging.error(f"⏰ Gemini API call timed out after {timeout} seconds.")
        except Exception as e:
            logging.error(f"❌ Gemini API error: {str(e)}")
        wait_time = delay * (2 ** attempt)
        logging.info(f"⏳ Waiting {wait_time}s before retry attempt {attempt + 2}")
        time.sleep(wait_time)
        attempt += 1
    logging.critical("❌ All Gemini API retry attempts failed.")
    return None

# ---------------------------
# Utility Functions
# ---------------------------

def api_response(message, status=200):
    return jsonify({'response': message}), status

def format_markdown_response(text):
    if not text or text.startswith("❌"):
        return text
    html = markdown.markdown(text, extensions=['extra', 'fenced_code'])
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
    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("Received response from Gemini AI.")
            return format_markdown_response(text)
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

# ---------------------------
# Dashboard & Feature Routes
# ---------------------------

@app.route('/')
def index_redirect():
    return render_template('sisu.html')

@app.route('/patient-dashboard', methods=['GET', 'POST'])
def patient_dashboard_reminders():
    if request.method == 'POST':
        email = request.form['email']
        med_name = request.form['med_name']
        time_str = request.form['reminder_time']
        try:
            hour, minute = map(int, time_str.split(':'))
            now = datetime.now()
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reminder_time < now:
                reminder_time += timedelta(days=1)
            reminders.append({
                'email': email,
                'med_name': med_name,
                'time': reminder_time,
                'sent': False
            })
            return redirect(url_for('reminders_page'))
        except Exception as e:
            return f"Invalid time format: {e}"
    return render_template('patient-dashboard.html')

@app.route('/reminders')
def reminders_page():
    return render_template('reminders.html', reminders=reminders)

@app.route('/sisu.html')
def sisu():
    return render_template('sisu.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/doctor-dashboard.html')
def doctor_dashboard():
    return render_template('doctor-dashboard.html')

@app.route('/pharmacist-dashboard.html')
def pharmacist_dashboard():
    return render_template('pharmacist-dashboard.html')

@app.route('/student-dashboard.html')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/drug-info-page')
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
def upload_image_page():
    return render_template('upload_image.html')

@app.route('/my-account')
def my_account():
    return render_template('my_account.html', user={"name": "Demo User", "email": "demo@example.com", "notifications": True})

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
        symptoms = data.get('symptoms')
        if not symptoms:
            logging.warning("❌ No symptoms provided.")
            return api_response('❌ No symptoms provided.', 400)
        result = get_symptom_recommendation(symptoms)
        return api_response(result)
    except Exception as e:
        logging.error(f"❌ Exception in /symptom_checker: {str(e)}")
        return api_response(f'❌ Error during analysis: {str(e)}', 500)

@app.route('/process-upload', methods=['POST'])
def process_upload():
    image_data = request.form.get("image_data")
    if image_data:
        result = analyze_image_with_gemini(image_data)
        return render_template("upload_image.html", result=result)
    else:
        return render_template("upload_image.html", result="❌ No image data received.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
