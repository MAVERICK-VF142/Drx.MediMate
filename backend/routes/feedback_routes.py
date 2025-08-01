from flask import Blueprint, render_template, request, redirect, url_for
import json
import os

feedback_bp = Blueprint('feedback', __name__, template_folder='../templates')

FEEDBACK_FILE = 'feedback.json'

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = {
            'role': request.form.get('role'),
            'name': request.form.get('name'),
            'rating': request.form.get('rating'),
            'message': request.form.get('message')
        }

        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as f:
                existing = json.load(f)
        else:
            existing = []

        existing.append(data)

        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(existing, f, indent=4)

        return render_template('feedback.html', message="✅ Thank you for your feedback!")

    return render_template('feedback.html')
