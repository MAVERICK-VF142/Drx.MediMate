from flask import jsonify

def api_response(message, status=200):
    """Standard JSON response helper"""
    return jsonify({'response': message}), status