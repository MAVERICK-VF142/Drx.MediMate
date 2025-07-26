import os
import json
import base64
import uuid
import secrets
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import markdown
import logging
import time
import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import firebase_admin
from firebase_admin import credentials, firestore

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
app.secret_key = os.getenv("SECRET_KEY", "dev_key_replace_in_production")
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize Firebase Admin SDK
try:
    # Check if Firebase Admin SDK is already initialized
    firebase_admin.get_app()
except ValueError:
    # If not initialized, initialize with default credentials
    # In production, set up proper credentials
    if os.path.exists('firebase-credentials.json'):
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

# Get Firestore database instance
db = firestore.client()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------
# Authentication Decorators
# ---------------------------

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated via session
        if 'user_id' not in session:
            # Redirect to login page
            logging.warning("Unauthorized access attempt to protected route")
            return redirect(url_for('sisu'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and is an admin
        if 'user_id' not in session:
            logging.warning("Unauthorized access attempt to admin route")
            return redirect(url_for('sisu'))
        
        if session.get('role') != 'admin':
            logging.warning(f"Non-admin user tried to access admin route. User role: {session.get('role')}")
            return render_template('unauthorized.html', message="Admin privileges required"), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Retry Helper Function
# ---------------------------

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
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/doctor-dashboard.html')
@login_required
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('dashboard'))
    return render_template('doctor-dashboard.html')

@app.route('/pharmacist-dashboard.html')
@login_required
def pharmacist_dashboard():
    if session.get('role') != 'pharmacist':
        return redirect(url_for('dashboard'))
    return render_template('pharmacist-dashboard.html')

@app.route('/student-dashboard.html')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    return render_template('student-dashboard.html')

@app.route('/patient-dashboard.html')
@login_required
def patient_dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('dashboard'))
    return render_template('patient-dashboard.html')

@app.route('/admin-dashboard.html')
@admin_required
def admin_dashboard():
    return render_template('admin-dashboard.html')


# ---------------------------
# Feature Page Routes
# ---------------------------

@app.route('/drug-info-page')
@login_required
def drug_info_page():
    return render_template('drug_info.html')

@app.route('/symptom-checker-page')
@login_required
def symptom_checker_page():
    return render_template('symptom_checker.html')

@app.route('/upload-image-page')
@login_required
def upload_image_page():
    return render_template('upload_image.html')

@app.route('/my-account')
@login_required
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })

# Additional feature routes that may be referenced in the dashboard
@app.route('/inventory-management')
@login_required
def inventory_management():
    return render_template('inventory_management.html')

@app.route('/prescription-processing')
@login_required
def prescription_processing():
    return render_template('prescription_processing.html')

@app.route('/patient-records')
@login_required
def patient_records():
    return render_template('patient_records.html')

@app.route('/educational-resources')
@login_required
def educational_resources():
    return render_template('educational_resources.html')

@app.route('/medication-tracker')
@login_required
def medication_tracker():
    return render_template('medication_tracker.html')

# ---------------------------
# Authentication API Endpoints
# ---------------------------

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle login requests from the frontend"""
    try:
        data = request.get_json()
        # In production, verify with Firebase Admin SDK
        # For now, we'll just set session variables based on client claims
        
        user_id = data.get('uid')
        email = data.get('email')
        role = data.get('role')
        
        if not user_id or not email or not role:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
        # Store user info in session
        session['user_id'] = user_id
        session['email'] = email
        session['role'] = role
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Handle logout requests"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check authentication status"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True, 
            'user_id': session['user_id'],
            'role': session.get('role')
        })
    return jsonify({'authenticated': False})

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
        print(result)
        return jsonify({'result': result})
    else:
        logging.warning("❌ No image data received in request")
    return jsonify({'result': '❌ No image received from camera.'})

# ---------------------------
# Admin Management Functions
# ---------------------------

def generate_invitation_code():
    """Generate a secure random invitation code for admin access"""
    return secrets.token_urlsafe(16)

def create_admin_invitation(email, expiry_hours=48):
    """Create an admin invitation with an expiry time"""
    invitation_id = str(uuid.uuid4())
    invitation_code = generate_invitation_code()
    
    current_time = datetime.datetime.now()
    expiry_time = current_time + datetime.timedelta(hours=expiry_hours)
    
    # Create invitation data for Firestore
    invitation_data = {
        'id': invitation_id,
        'email': email,
        'code': invitation_code,
        'created_at': current_time,
        'expires_at': expiry_time,
        'used': False
    }
    
    # Add to Firestore
    db.collection('admin_invitations').document(invitation_code).set(invitation_data)
    
    return invitation_code

def verify_admin_invitation(code):
    """Verify if an admin invitation code is valid"""
    # Get invitation from Firestore
    invitation_ref = db.collection('admin_invitations').document(code)
    invitation_doc = invitation_ref.get()
    
    if not invitation_doc.exists:
        return False, "Invalid invitation code"
    
    invitation = invitation_doc.to_dict()
    
    # Check if already used
    if invitation['used']:
        return False, "Invitation code has already been used"
    
    # Check if expired
    expires_at = invitation['expires_at']
    if isinstance(expires_at, datetime.datetime) and datetime.datetime.now() > expires_at:
        return False, "Invitation code has expired"
    
    return True, invitation

# ---------------------------
# Admin API Endpoints
# ---------------------------

@app.route('/api/admin/invitation', methods=['POST'])
@admin_required
def create_invitation():
    """Create an invitation code for a new admin user"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
            
        invitation_code = create_admin_invitation(email)
        
        return jsonify({
            'success': True, 
            'invitation_code': invitation_code,
            'message': f'Invitation created for {email}'
        })
    except Exception as e:
        logging.error(f"Error creating admin invitation: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/verify-invitation', methods=['POST'])
def verify_invitation():
    """Verify an admin invitation code"""
    try:
        data = request.get_json()
        code = data.get('code')
        email = data.get('email')
        
        if not code or not email:
            return jsonify({'success': False, 'message': 'Code and email are required'}), 400
            
        is_valid, invitation = verify_admin_invitation(code)
        
        if is_valid:
            # Check if the invitation is for this email
            if invitation['email'].lower() != email.lower():
                return jsonify({'success': False, 'message': 'This invitation is not for this email address'}), 400
                
            # Mark as used
            invitation_ref = db.collection('admin_invitations').document(code)
            invitation_ref.update({'used': True})
            
            return jsonify({'success': True, 'message': 'Invitation code is valid'})
        else:
            return jsonify({'success': False, 'message': invitation}), 400
    except Exception as e:
        logging.error(f"Error verifying admin invitation: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/invitations', methods=['GET'])
@admin_required
def list_invitations():
    """List all admin invitations"""
    try:
        invitations_ref = db.collection('admin_invitations').stream()
        invitations_list = [invite.to_dict() for invite in invitations_ref]
        
        # Convert datetime objects to ISO strings for JSON serialization
        for invitation in invitations_list:
            if isinstance(invitation.get('created_at'), datetime.datetime):
                invitation['created_at'] = invitation['created_at'].isoformat()
            if isinstance(invitation.get('expires_at'), datetime.datetime):
                invitation['expires_at'] = invitation['expires_at'].isoformat()
        
        return jsonify({
            'success': True,
            'invitations': invitations_list
        })
    except Exception as e:
        logging.error(f"Error listing admin invitations: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

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