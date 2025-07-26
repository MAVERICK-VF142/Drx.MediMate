import os
import logging
import time
import base64
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from io import BytesIO
from PIL import Image
import google.generativeai as genai


# Import configuration
from config import Config

# ---------------------------
# Language Mapping
# ---------------------------
LANGUAGE_CODES = {
    "English": "en",
    "Assamese": "as",
    "Bengali": "bn",
    "Bodo": "brx", # Note: Bodo might not have a direct ISO 639-1, check deep_translator docs for best fit or use 'auto'
    "Dogri": "doi", # Similar note for Dogri
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Kashmiri": "ks",
    "Konkani": "kok", # Similar note for Konkani
    "Maithili": "mai", # Similar note for Maithili
    "Malayalam": "ml",
    "Manipuri": "mni", # Similar note for Manipuri
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia": "or",
    "Punjabi": "pa",
    "Sanskrit": "sa",
    "Santali": "sat", # Similar note for Santali
    "Sindhi": "sd",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur"
}

INDIAN_LANGUAGES = list(LANGUAGE_CODES.keys())

# ---------------------------
# Gemini API Configuration
# ---------------------------
# Configure Gemini API using the key from Config
genai.configure(api_key=Config.GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def gemini_generate_with_retry(prompt, max_retries=3, delay=2, timeout=10):
    """
    Calls Gemini API with timeout and retry logic.
    - Retries failed calls (with exponential backoff)
    - Aborts slow responses gracefully
    """
    attempt = 0
    while attempt < max_retries:
        try:
            logging.info(f"🌐 Gemini API Call Attempt {attempt + 1}")

            # Set up timeout using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                response = future.result(timeout=timeout)  # Timeout in seconds

            # Check if response is valid
            if response and hasattr(response, 'text') and response.text.strip():
                logging.info("✅ Gemini API call successful.")
                return response
            else:
                logging.warning("⚠️ Empty or malformed response. Retrying...")

        except FuturesTimeout:
            logging.error(f"⏰ Gemini API call timed out after {timeout} seconds.")
        except Exception as e:
            logging.error(f"❌ Gemini API error: {str(e)}")

        # Backoff delay before retry
        wait_time = delay * (2 ** attempt)  # 2s, 4s, 8s...
        logging.info(f"⏳ Waiting {wait_time}s before retry attempt {attempt + 2}")
        time.sleep(wait_time)
        attempt += 1

    logging.critical("❌ All Gemini API retry attempts failed.")
    return None

# ---------------------------
# AI Functions
# ---------------------------

def get_drug_information(drug_name):
    """
    Generates a clinical summary for a given drug.
    Ensures output is in bullet points.
    """
    prompt = (
        f"Provide a brief clinical summary for pharmacists on the drug {drug_name}, formatted as a bulleted list:\n"
        "- Therapeutic uses\n"
        "- Standard dosage\n"
        "- Common & serious side effects\n"
        "- Contraindications\n"
        "- Important drug interactions\n"
        "Ensure each point starts on a new line with a bullet (e.g., '-'). Answer concisely."
    )
    logging.info(f"Prompt to Gemini: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        logging.info("Received response from Gemini AI.")
        if response and hasattr(response, 'text'):
            # Post-process to ensure bullet points if Gemini doesn't strictly adhere
            text = response.text.strip()
            # Simple check/fix: if lines don't start with a bullet, add one
            formatted_lines = []
            for line in text.split('\n'):
                line = line.strip()
                if line: # Only process non-empty lines
                    if not line.startswith(('-', '*')):
                        formatted_lines.append(f"- {line}")
                    else:
                        formatted_lines.append(line)
            return "\n".join(formatted_lines)
        else:
            logging.warning("No text in AI response for drug info.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"Exception in get_drug_information: {str(e)}")
        return f"❌ Error: {str(e)}"

def get_symptom_recommendation(symptoms):
    """
    Generates OTC recommendations for symptoms, formatted as bullet points.
    """
    prompt = (
        f"Given the symptoms: {symptoms}, recommend over-the-counter treatment options, formatted as a bulleted list.\n"
        "Include:\n"
        "- Common side effects of recommended treatments\n"
        "- Important interactions\n"
        "- Safety tips\n"
        "If symptoms suggest a medical emergency or severe condition, recommend immediate doctor consultation.\n"
        "Ensure each point starts on a new line with a bullet (e.g., '-'). Respond concisely without disclaimers."
    )
    logging.info(f"Prompt to Gemini for symptom check: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        logging.info("Received response from Gemini for symptoms.")
        if response and hasattr(response, 'text'):
            # Post-process to ensure bullet points if Gemini doesn't strictly adhere
            text = response.text.strip()
            formatted_lines = []
            for line in text.split('\n'):
                line = line.strip()
                if line: # Only process non-empty lines
                    if not line.startswith(('-', '*')):
                        formatted_lines.append(f"- {line}")
                    else:
                        formatted_lines.append(line)
            return "\n".join(formatted_lines)
        else:
            logging.warning("❌ No text in AI response for symptoms.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in get_symptom_recommendation: {str(e)}")
        return f"❌ Error: {str(e)}"

def analyze_image_with_gemini(image_data):
    """
    Analyzes an image of medicine packaging using Gemini Vision.
    """
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return "❌ Invalid image format uploaded."

        logging.info("Decoding and processing image for AI analysis...")
        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "Analyze this image of a medicine or drug packaging. "
            "Identify the drug name, manufacturer (if visible), and give a brief clinical summary, formatted as a bulleted list. "
            "If the image is blurry or unclear, politely ask the user to retake it."
            "Ensure each point starts on a new line with a bullet (e.g., '-')."
        )

        logging.info("Sending prompt and image to Gemini AI.")
        response = gemini_generate_with_retry([prompt, image])
        text = response.text.strip() if response and hasattr(response, 'text') else None
        if not text:
            logging.warning("❌ Analysis failed or empty AI response.")
            return "❌ Analysis failed or empty response from AI."

        # Post-process to ensure bullet points if Gemini doesn't strictly adhere
        formatted_lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line: # Only process non-empty lines
                if not line.startswith(('-', '*')):
                    formatted_lines.append(f"- {line}")
                else:
                    formatted_lines.append(line)
        return "\n".join(formatted_lines)

    except Exception as e:
        logging.error(f"❌ Error during image analysis: {str(e)}")
        return f"❌ Error during image analysis: {str(e)}"
