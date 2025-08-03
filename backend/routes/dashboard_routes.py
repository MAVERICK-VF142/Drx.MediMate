from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/patient_dashboard')
@login_required
def patient_dashboard():
    mongo = current_app.mongo
    user = mongo.db.users.find_one({'email': current_user.email})
    if not user:
        return {"error": "User not found"}, 404
    user_data = {
        'email': user['email'],
        'role': user.get('role', 'patient'),
        'name': user.get('name', 'N/A'),
    }
    return render_template('patient_dashboard.html', user=user_data)

@dashboard_bp.route('/my-account')
@login_required
def my_account():
    mongo = current_app.mongo
    user = mongo.db.users.find_one({'email': current_user.email})
    if not user:
        return {"error": "User not found"}, 404
    user_data = {
        'name': user.get('name', 'N/A'),
        'email': user['email'],
        'notifications': user.get('notifications', True)
    }
    return render_template('my_account.html', user=user_data)