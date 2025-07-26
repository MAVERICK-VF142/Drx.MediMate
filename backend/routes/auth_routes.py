from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index_redirect():
    # Redirect to login page
    return render_template('sisu.html')

@auth_bp.route('/sisu.html')
def sisu():
    return render_template('sisu.html')
