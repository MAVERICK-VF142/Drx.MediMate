import base64
from PIL import Image
from io import BytesIO
# from flask import current_app

def analyze_image_with_gemini_service(image_data, gemini_model):
    
    if gemini_model is None:
        return "⚠️ AI features are not active (GEMINI_KEY missing). Cannot analyze image."
    try:
        if not image_data.startswith("data:image/"):
            return "❌ Invalid image format uploaded."

        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "Analyze this image of a medicine or drug packaging. "
            "Identify the drug name, manufacturer (if visible), and give a brief clinical summary. "
            "If the image is blurry or unclear, politely ask the user to retake it."
        )

        response = gemini_model.generate_content([prompt, image]) # Use passed model
        text = response.text.strip() if response and hasattr(response, 'text') else None
        if not text:
            return "❌ Analysis failed or empty response from AI."
        return text

    except Exception as e:
        return f"❌ Error during image analysis: {str(e)}"