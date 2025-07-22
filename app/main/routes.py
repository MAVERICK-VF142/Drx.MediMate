from flask import render_template
from . import main_bp # Import the blueprint instance

@main_bp.route('/')
def sisu():
    return render_template('main/sisu.html') # Update template path

@main_bp.route('/index.html')
def index():
    return render_template('main/index.html') # Update template path
