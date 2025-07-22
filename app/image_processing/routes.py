from flask import render_template, request, current_app
from . import image_processing_bp
from .services import analyze_image_with_gemini_service 
# from app.utils.helpers import api_response # This would be imported if needed

@image_processing_bp.route('/upload-image-page')
def upload_image_page():
    return render_template('main/upload_image.html') 

@image_processing_bp.route('/process-upload', methods=['POST'])
def process_upload():
    try:
        image_data = request.form.get("image_data")
        if not image_data:
            return render_template("main/upload_image.html", result="❌ No image data received.")

        result_message = analyze_image_with_gemini_service(image_data, current_app.gemini_model)
        
        return render_template("main/upload_image.html", result=result_message)

    except Exception as e:
        return render_template("main/upload_image.html", result=f"❌ An internal error occurred: {str(e)}")