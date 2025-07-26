from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)


# ---------------------------
# Error Handlers
# ---------------------------

@errors_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@errors_bp.app_errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
