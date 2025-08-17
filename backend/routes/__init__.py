from .ai_routes import ai_bp
from .api_routes import api_bp
def register_blueprints(app):
    app.register_blueprint(ai_bp) 
    
def register_blueprints(app):
    app.register_blueprint(api_bp)