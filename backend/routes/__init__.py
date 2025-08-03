from .api_routes import api_bp
from .ai_routes import ai_bp
from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .feature_routes import feature_bp
from .error_handlers import error_bp
from .admin_routes import admin_bp  # 👈 Add this line

def register_blueprints(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(feature_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(admin_bp)  # 👈 And this line
