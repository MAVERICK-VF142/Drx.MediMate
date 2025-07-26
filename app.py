# Standard library imports
import base64
import datetime
import functools
import json
import logging
import os
import re
import secrets
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from io import BytesIO

# Third-party imports
import firebase_admin
import google.generativeai as genai
import markdown
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, auth
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image

# Local application imports
from utils.cache import get_cached_drug, set_cached_drug

# Load environment variables once, right after imports
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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

def get_limiter_key():
    """
    Custom key function for rate limiting that uses:
    - Authenticated user's ID if available
    - Falls back to IP address for anonymous users
    """
    if 'user' in session:
        return f"user:{session['user']['id']}"
    return get_remote_address()

# Initialize rate limiter with Redis in production, memory otherwise
storage_uri = os.environ.get('REDIS_URL', 'memory://')
limiter = Limiter(
    key_func=get_limiter_key,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=storage_uri,
    strategy="fixed-window"  # More consistent rate limiting
)
# Configure Flask secret key
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    logging.warning("SECRET_KEY environment variable not set. Generating a temporary random key. This should ONLY be used for local development.")
    secret_key = secrets.token_urlsafe(32)
app.secret_key = secret_key
# Configure CORS with restricted origins for production
allowed_origins = os.getenv("ALLOWED_ORIGINS")
if allowed_origins:
    origins = allowed_origins.split(",")
else:
    # Default to localhost for development
    origins = [
        "http://localhost:5000", 
        "http://127.0.0.1:5000",
        "http://localhost:8000", # Common alternative dev port
        "http://127.0.0.1:8000"
    ]
logging.info(f"CORS enabled for origins: {origins}")
CORS(app, origins=origins, supports_credentials=True)
# ---------------------------
# Firebase Admin SDK Setup
# ---------------------------
# You can specify a credentials file via the FIREBASE_CREDENTIALS_PATH env var.
# If not provided, will look for firebase-credentials.json in the project root.
# Fallback to Application Default Credentials *only* for local dev.
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_JSON", "firebase-credentials.json")

try:
    firebase_admin.get_app()
    logging.info("Firebase Admin SDK already initialized.")
except ValueError:
    try:
        # First, check for credentials JSON via environment variable (for production like Vercel)
        cred_json = os.getenv("FIREBASE_CREDENTIALS")
        if cred_json:
            logging.info("Initializing Firebase Admin SDK with credentials from FIREBASE_CREDENTIALS environment variable.")
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        elif os.path.exists(firebase_credentials_path):
            logging.info(f"Initializing Firebase Admin SDK with credentials at: {firebase_credentials_path}")
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
        else:
            logging.warning(
                "Firebase credentials file not found. Attempting to initialize with Application Default Credentials. "
                "Set FIREBASE_CREDENTIALS_PATH or provide firebase-credentials.json for production deployments."
            )
            firebase_admin.initialize_app()
    except Exception as fb_err:
        logging.error(f"❌ Failed to initialize Firebase Admin SDK: {fb_err}")
        # Re-raise so the app fails fast instead of running in a bad state
        raise

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

def parse_firestore_timestamp(timestamp):
    """
    Safely parses a Firestore timestamp which can be a datetime object,
    a Firestore Timestamp, or an ISO string.
    """
    if isinstance(timestamp, datetime.datetime):
        return timestamp
    if hasattr(timestamp, 'to_datetime'):
        try:
            return timestamp.to_datetime()
        except Exception as e:
            logging.error(f"Failed to convert Firestore Timestamp to datetime: {e}")
            return None
    if isinstance(timestamp, str):
        try:
            return datetime.datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            logging.error(f"Could not parse timestamp string: {timestamp}")
            return None
    logging.warning(f"Unhandled timestamp type: {type(timestamp)}")
    return None

def validate_drug_name(drug_name):
    """
    Validates the drug name to ensure it meets security and format requirements.
    - Allows alphanumeric characters, spaces, hyphens, and parentheses.
    - Requires a minimum of 2 non-whitespace characters.
    - Limits the length to 100 characters.
    
    Args:
        drug_name (str): The drug name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check for empty or whitespace-only input
    if not drug_name or not drug_name.strip():
        return False
        
    # Strip whitespace and check length constraints
    stripped = drug_name.strip()
    if len(stripped) < 2 or len(drug_name) > 100:
        return False
        
    # Regex to allow alphanumeric, spaces, hyphens, and parentheses only
    if not re.match(r'^[a-zA-Z0-9\s\-\(\)]+$', stripped):
        return False
        
    return True

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
        id_token = data.get('idToken')

        if not id_token:
            return jsonify({'success': False, 'message': 'ID token is required'}), 400

        # Verify the ID token with Firebase Admin SDK
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as verify_err:
            logging.error(f"Token verification failed: {verify_err}")
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        user_id = decoded_token.get('uid')
        email = decoded_token.get('email')

        # Attempt to get role from custom claims first
        role = decoded_token.get('role')

        # If role is not set in custom claims, look it up in Firestore
        if not role:
            try:
                user_doc = db.collection('users').document(user_id).get()
                if user_doc.exists:
                    role = user_doc.to_dict().get('role')
            except Exception as fs_err:
                logging.error(f"Error retrieving user role from Firestore: {fs_err}")

        if not role:
            logging.warning(f"Role not found for user {user_id}")
            return jsonify({'success': False, 'message': 'User role not found'}), 403

        # Store user info in session after successful verification
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
@limiter.limit("10 per minute")
def get_drug_info():
    logging.info("API /get_drug_info called")
    try:
        data = request.get_json()
        logging.info(f"Request JSON: {data}")
        drug_name = data.get('drug_name')
        if drug_name is None:
            logging.warning("❌ Missing drug name in request.")
            return api_response('❌ Missing drug name.', 400)
        if not validate_drug_name(drug_name):
            logging.warning(f"❌ Invalid drug name received: {drug_name}")
            return api_response('❌ Invalid drug name.', 400)
        logging.info(f"Calling get_drug_information with drug_name: {drug_name}")
        response = get_drug_information(drug_name)
        return api_response(response)
    except Exception as e:
        logging.error(f"Exception in /get_drug_info: {str(e)}")
        return api_response(f"❌ Error: {str(e)}", 500)

@app.route('/symptom_checker', methods=['POST'])
@limiter.limit("10 per minute")
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
@limiter.limit("10 per minute")
def process_upload():
    logging.info("API /process-upload called")
    image_data = request.form.get("image_data")
    if image_data:
        logging.info("Image data received for analysis")
        result = analyze_image_with_gemini(image_data)
        logging.info(f"Image analysis result: {result}")
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
    expires_at_raw = invitation.get('expires_at')
    expires_at = parse_firestore_timestamp(expires_at_raw)
    if not expires_at:
        return False, "Invalid expiry date format"

    if datetime.datetime.now() > expires_at:
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
    """Verify an admin invitation code atomically using a Firestore transaction"""
    try:
        data = request.get_json()
        code = data.get('code')
        email = data.get('email')

        if not code or not email:
            return jsonify({'success': False, 'message': 'Code and email are required'}), 400

        invitation_ref = db.collection('admin_invitations').document(code)
        transaction = db.transaction()

        @firestore.transactional
        def _verify_and_use_invitation(txn):
            snapshot = invitation_ref.get(transaction=txn)
            if not snapshot.exists:
                return False, "Invalid invitation code"

            invitation = snapshot.to_dict()

            # Validate email match
            if invitation['email'].lower() != email.lower():
                return False, "This invitation is not for this email address"

            # Already used
            if invitation.get('used'):
                return False, "Invitation code has already been used"

            # Expiration check
            expires_at_raw = invitation.get('expires_at')
            expires_at = parse_firestore_timestamp(expires_at_raw)
            if not expires_at:
                return False, "Invalid expiry date format"
            if datetime.datetime.now() > expires_at:
                return False, "Invitation code has expired"

            # All checks passed – mark as used within the same transaction
            txn.update(invitation_ref, {'used': True})
            return True, invitation

        success, result = _verify_and_use_invitation(transaction)
        if success:
            return jsonify({'success': True, 'message': 'Invitation code is valid'})
        else:
            return jsonify({'success': False, 'message': result}), 400

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
