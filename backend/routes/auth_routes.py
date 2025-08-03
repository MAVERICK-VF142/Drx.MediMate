from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

def create_user(email, password, role="patient"):
    mongo = current_app.mongo
    hashed_password = generate_password_hash(password)
    mongo.db.users.insert_one({'email': email, 'password': hashed_password, 'role': role})

def find_user_by_email(email):
    mongo = current_app.mongo
    return mongo.db.users.find_one({'email': email})

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

@auth_bp.route('/')
def index_redirect():
    return redirect(url_for('auth.sisu'))

@auth_bp.route('/sisu', methods=['GET', 'POST'])
def sisu():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = find_user_by_email(email)
        if user and verify_password(user['password'], password):
            flash('Login successful!', 'success')
            role = user.get('role', 'patient').lower()
            if role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('dashboard.patient_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('sisu.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'patient')
        if find_user_by_email(email):
            flash('User already exists.', 'warning')
        else:
            create_user(email, password, role)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.sisu'))
    return render_template('register.html')