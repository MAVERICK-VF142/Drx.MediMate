from flask import Blueprint, render_template

feature_bp = Blueprint('features', __name__)


# ---------------------------
# Feature Page Routes
# ---------------------------


@feature_bp.route('/drug-info-page')
def drug_info():
    return render_template('drug_info.html')

@feature_bp.route('/symptom-checker-page')
def symptom_checker():
    return render_template('symptom_checker.html')

@feature_bp.route('/upload-image-page')
def upload_image():
    return render_template('upload_image.html')

@feature_bp.route('/prescription-validator-page')
def prescription_validator():
    return render_template('prescription_validator.html')

@feature_bp.route('/my-account')
def my_account():
    return render_template('my_account.html', user={
        "name": "Demo User",
        "email": "demo@example.com",
        "notifications": True
    })


# Additional feature routes that may be referenced in the dashboard

@feature_bp.route('/inventory-management')
def inventory():
    return render_template('inventory_management.html')

@feature_bp.route('/prescription-processing')
def prescription():
    return render_template('prescription_processing.html')

@feature_bp.route('/patient-records')
def records():
    return render_template('patient_records.html')

@feature_bp.route('/educational-resources')
def resources():
    return render_template('educational_resources.html')

@feature_bp.route('/medication-tracker')
def tracker():
    return render_template('medication_tracker.html')
