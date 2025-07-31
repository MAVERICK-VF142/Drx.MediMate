"""
Enhanced error handling middleware for Drx.MediMate
Provides structured error responses and logging
"""

import logging
import traceback
from flask import jsonify, request
from functools import wraps
import time

# Configure logger
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API Error class"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

class ValidationError(APIError):
    """Validation specific error"""
    def __init__(self, message, field=None):
        super().__init__(message, status_code=400)
        if field:
            self.payload = {'field': field}

class RateLimitError(APIError):
    """Rate limiting error"""
    def __init__(self, message="Too many requests", retry_after=60):
        super().__init__(message, status_code=429)
        self.payload = {'retry_after': retry_after}

def handle_api_error(error):
    """Handle custom API errors"""
    logger.error(f"API Error: {error.message}")
    
    response = {
        'error': True,
        'message': error.message,
        'status_code': error.status_code,
        'timestamp': time.time()
    }
    
    if error.payload:
        response.update(error.payload)
        
    return jsonify(response), error.status_code

def handle_validation_error(error):
    """Handle validation errors specifically"""
    logger.warning(f"Validation Error: {error.message}")
    
    response = {
        'error': True,
        'type': 'validation_error',
        'message': error.message,
        'status_code': 400,
        'timestamp': time.time()
    }
    
    if 'field' in error.payload:
        response['field'] = error.payload['field']
        
    return jsonify(response), 400

def handle_internal_error(error):
    """Handle unexpected internal errors"""
    error_id = str(int(time.time()))
    logger.error(f"Internal Error [{error_id}]: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Don't expose internal error details in production
    response = {
        'error': True,
        'type': 'internal_error',
        'message': 'An internal error occurred. Please try again later.',
        'error_id': error_id,
        'status_code': 500,
        'timestamp': time.time()
    }
    
    return jsonify(response), 500

def handle_gemini_api_error(error):
    """Handle Gemini API specific errors"""
    logger.error(f"Gemini API Error: {str(error)}")
    
    response = {
        'error': True,
        'type': 'ai_service_error',
        'message': 'AI service is temporarily unavailable. Please try again.',
        'status_code': 503,
        'timestamp': time.time()
    }
    
    return jsonify(response), 503

def rate_limit(max_requests=60, window_seconds=60):
    """
    Rate limiting decorator
    Usage: @rate_limit(max_requests=30, window_seconds=60)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (consider Redis for production)
            if not hasattr(decorated_function, 'requests'):
                decorated_function.requests = {}
            
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            decorated_function.requests = {
                ip: timestamps for ip, timestamps in decorated_function.requests.items()
                if any(t > current_time - window_seconds for t in timestamps)
            }
            
            # Check rate limit
            if client_ip in decorated_function.requests:
                timestamps = [t for t in decorated_function.requests[client_ip] 
                            if t > current_time - window_seconds]
                if len(timestamps) >= max_requests:
                    raise RateLimitError(retry_after=window_seconds)
                decorated_function.requests[client_ip] = timestamps + [current_time]
            else:
                decorated_function.requests[client_ip] = [current_time]
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_input(required_fields=None):
    """
    Validate JSON input decorator
    Usage: @validate_json_input(['drug_name', 'dosage'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request must contain valid JSON")
            
            data = request.get_json()
            if not data:
                raise ValidationError("Request body cannot be empty")
            
            if required_fields:
                missing_fields = [field for field in required_fields if not data.get(field)]
                if missing_fields:
                    raise ValidationError(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        field=missing_fields[0]
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request_info():
    """Decorator to log request information"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            logger.info(f"API Request: {request.method} {request.path}")
            logger.info(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
            logger.info(f"IP: {request.remote_addr}")
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Request completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Request failed after {duration:.2f}s: {str(e)}")
                raise
                
        return decorated_function
    return decorator

def init_error_handlers(app):
    """Initialize all error handlers for the Flask app"""
    
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(RateLimitError, handle_api_error)
    app.register_error_handler(500, handle_internal_error)
    
    # Handle specific exceptions
    app.register_error_handler(Exception, handle_internal_error)
    
    logger.info("Error handlers initialized successfully")
