from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/index.html')
def index():
    return render_template('index.html')

# Alternative route for index
@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('index.html')


# Role-specific Dashboard Routes
@dashboard_bp.route('/doctor-dashboard.html')
def doctor_dashboard():
    return render_template('doctor-dashboard.html')

@dashboard_bp.route('/pharmacist-dashboard.html')
def pharmacist_dashboard():
    return render_template('pharmacist-dashboard.html')

@dashboard_bp.route('/student-dashboard.html')
def student_dashboard():
    return render_template('student-dashboard.html')

@dashboard_bp.route('/patient-dashboard.html')
def patient_dashboard():
    return render_template('patient-dashboard.html')
