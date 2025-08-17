import base64
import os
import io
import re
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from google.generativeai.types import content_types
import markdown
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from cachetools import TTLCache
import threading
import json

# A cache with maxsize 100 items, and TTL of 600 seconds (10 minutes)
drug_cache = TTLCache(maxsize=100, ttl=600)

# Lock to prevent race conditions in threaded environments (e.g., Flask)
cache_lock = threading.Lock()


def get_cached_drug(drug_name):
    key = drug_name.strip().lower()
    with cache_lock:
        return drug_cache.get(key)


def set_cached_drug(drug_name, response):
    key = drug_name.strip().lower()
    with cache_lock:
        drug_cache[key] = response


def format_markdown_response(text):
    """Convert Markdown text to HTML for consistent, readable output"""
    if not text or text.startswith("❌"):
        return text  # Return error messages as-is
    html = markdown.markdown(text, extensions=['extra', 'fenced_code'])
    return f'<div class="markdown-content">{html}</div>'


# Load API key from environment variable
genai.configure(api_key=os.getenv("GEMINI_KEY"))
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
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(model.generate_content, prompt)
                response = future.result(timeout=timeout)
            if response and hasattr(response, 'text') and response.text.strip():
                logging.info("✅ Gemini API call successful.")
                return response
            else:
                logging.warning("⚠️ Empty or malformed response. Retrying...")
        except FuturesTimeout:
            logging.error(f"⏰ Gemini API call timed out after {timeout} seconds.")
        except Exception as e:
            logging.error(f"❌ Gemini API error: {str(e)}")

        wait_time = delay * (2 ** attempt)
        logging.info(f"⏳ Waiting {wait_time}s before retry attempt {attempt + 2}")
        time.sleep(wait_time)
        attempt += 1

    logging.critical("❌ All Gemini API retry attempts failed.")
    return None


def get_drug_information(drug_name):
    prompt = (
        f"Provide a brief clinical summary for pharmacists on the drug **{drug_name}** in Markdown format:\n"
        "## Therapeutic Uses\n"
        "- List primary therapeutic uses\n"
        "## Standard Dosage\n"
        "- Provide standard adult dosage (include administration route and frequency)\n"
        "## Common Side Effects\n"
        "- List common side effects\n"
        "## Serious Side Effects\n"
        "- List serious side effects requiring immediate attention\n"
        "## Contraindications\n"
        "- List conditions or scenarios where the drug should not be used\n"
        "## Important Drug Interactions\n"
        "- List significant drug interactions\n"
        "Use concise bullet points. Ensure clarity and professional tone."
    )

    logging.info(f"Prompt to Gemini: {prompt}")

    cached = get_cached_drug(drug_name)
    if cached:
        logging.info(f"📦 Cache hit for drug: {drug_name}")
        return cached

    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            set_cached_drug(drug_name, text)
            logging.info("✅ Cached new drug info response.")
            return format_markdown_response(text)
        else:
            logging.warning("No text in AI response.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"Exception in get_drug_information: {str(e)}")
        return f"❌ Error: {str(e)}"


def get_symptom_recommendation(symptoms):
    prompt = (
        f"Given the symptoms: **{symptoms}**, recommend over-the-counter treatment options in Markdown format:\n"
        "## Recommended Over-the-Counter Treatments\n"
        "- List appropriate OTC medications or treatments\n"
        "## Common Side Effects\n"
        "- List common side effects of recommended treatments\n"
        "## Important Interactions\n"
        "- List significant drug or condition interactions\n"
        "## Safety Tips\n"
        "- Provide key safety tips or precautions\n"
        "If symptoms suggest a medical emergency or severe condition, clearly state: **'Seek immediate medical attention.'** "
        "Use concise bullet points in Markdown format. Avoid disclaimers."
    )

    logging.info(f"Prompt to Gemini for symptom check: {prompt}")
    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("Received response from Gemini for symptoms.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No text in AI response for symptoms.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in get_symptom_recommendation: {str(e)}")
        return f"❌ Error: {str(e)}"


def drug_side_effect_checker(drug_name):
    prompt = f'''
    You are a medical knowledge assistant that predicts drug side effects.

    Given the drug name: "{drug_name}", output ONLY a valid JSON object in the following format:

    {{
      "drug": "{drug_name}",
      "common_side_effects": [
        {{ "name": "Side effect name", "severity": "Mild|Moderate|Severe", "explanation": "Short medically accurate explanation" }}
      ],
      "rare_side_effects": [
        {{ "name": "Side effect name", "severity": "Mild|Moderate|Severe", "explanation": "Short medically accurate explanation" }}
      ]
    }}

    Guidelines:
    - Use reliable, evidence-based medical knowledge.
    - Separate common vs rare side effects clearly.
    - Classify severity as only "Mild", "Moderate", or "Severe".
    - Each explanation should be concise and factual (1-2 sentences).
    - Do not include any extra commentary or text outside the JSON.
    - If the drug is not recognized, return:
    {{
      "drug": "{drug_name}",
      "common_side_effects": [],
      "rare_side_effects": []
    }}
    '''

    

    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()

            # Clean up markdown if Gemini adds ```json
            if text.startswith("```"):
                text = re.sub(r"^```(json)?", "", text, flags=re.MULTILINE).strip()
                text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()


            try:
                return json.loads(text)
            except json.JSONDecodeError:
                logging.error(f"❌ JSON parsing failed for Gemini output: {text}")
                return {
                    "drug": drug_name,
                    "common_side_effects": [],
                    "rare_side_effects": []
                }
        else:
            logging.warning("❌ No text in AI response for drug side effects.")
            return {
                "drug": drug_name,
                "common_side_effects": [],
                "rare_side_effects": []
            }
    except Exception as e:
        logging.error(f"❌ Exception in drug_side_effect_checker: {str(e)}")
        return {
            "drug": drug_name,
            "common_side_effects": [],
            "rare_side_effects": [],
            "error": str(e)
        }


def analyze_image_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return "❌ Invalid image format uploaded."

        logging.info("Decoding and processing image for AI analysis...")
        image_base64 = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))

        prompt = (
            "Analyze this image of a medicine or drug packaging. Provide the response in Markdown format:\n"
            "## Drug Information\n"
            "- **Drug Name**: Identify the drug name (if visible)\n"
            "- **Manufacturer**: Identify the manufacturer (if visible)\n"
            "## Clinical Summary\n"
            "- **Therapeutic Uses**: List primary uses\n"
            "- **Standard Dosage**: Provide standard dosage\n"
            "- **Common Side Effects**: List common side effects\n"
            "- **Serious Side Effects**: List serious side effects\n"
            "- **Contraindications**: List contraindications\n"
            "- **Important Interactions**: List significant interactions\n"
            "If the image is blurry or unclear, respond with: **'Please retake the image for better clarity.'**"
        )

        logging.info("Sending prompt and image to Gemini AI.")
        response = gemini_generate_with_retry([prompt, image])

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("AI analysis complete.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ Analysis failed or empty AI response.")
            return "❌ Analysis failed or empty response from AI."

    except Exception as e:
        logging.error(f"❌ Error during image analysis: {str(e)}")
        return f"❌ Error during image analysis: {str(e)}"


def get_drug_comparison_summary(drug1, drug2):
    prompt = (
        f"Compare the drugs **{drug1}** and **{drug2}** side by side in a Markdown table.\n"
        "\nInclude the following aspects as rows:\n"
        "- Therapeutic Uses\n"
        "- Dosage\n"
        "- Common Side Effects\n"
        "- Serious Side Effects\n"
        "- Contraindications\n"
        "- Drug Interactions\n"
        "- Drug Class\n"
        "- Cost/Availability\n"
        "\nUse column headers: `Aspect`, `" + drug1 + "`, `" + drug2 + "`.\n"
        "Keep the output clean and do not include explanations outside the table."
    )

    logging.info(f"Prompt to Gemini (summary compare): {prompt}")
    response = gemini_generate_with_retry(prompt)
    if response and hasattr(response, 'text'):
        return response.text.strip()
    return "❌ Failed to generate comparison summary."


def analyze_prescription_with_gemini(image_data):
    try:
        if not image_data.startswith("data:image/"):
            logging.warning("❌ Invalid image format received.")
            return "❌ Invalid image format uploaded."

        logging.info("Decoding and processing prescription image for validation...")
        if "," in image_data:
            image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        prompt = (
            "You are a medical assistant AI.\n"
            "Given an image of a *prescription*, extract and analyze:\n\n"
            "### Step 1: Extract Prescription Details\n"
            "- List all *medications/drugs* mentioned.\n"
            "- Include *dosage, **frequency, and **duration* if visible.\n\n"
            "### Step 2: Validation\n"
            "- Check for *duplicate drugs* or overlapping medicines.\n"
            "- Check for *drug-drug interactions*.\n"
            "- Flag any *potentially harmful combinations*.\n"
            "- If dosage looks too high or low, *flag it*.\n\n"
            "### Output Format (Markdown)\n"
            "## Extracted Prescription\n"
            "- Drug 1: [Name], [Dosage], [Frequency], [Duration]\n"
            "- ...\n\n"
            "## AI-Powered Feedback\n"
            "- Safety Warnings:\n"
            "- Interaction Notes:\n"
            "- Suggestions:\n\n"
            "If the image is unclear or handwriting is illegible, reply with:\n"
            "'⚠ The prescription image is too unclear to read. Please retake it in good lighting.'"
        )

        logging.info("Sending prescription image to Gemini for validation...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        if response is not None:
            logging.info(f"Gemini Raw Response: {response}")
        else:
            logging.warning("⚠ Gemini response is None.")

        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("✅ Prescription validation complete.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No response or empty output from Gemini.")
            return "❌ No useful output received from Gemini."

    except Exception as e:
        logging.error(f"❌ Error during image analysis: {str(e)}")
        return f"❌ Error during image analysis: {str(e)}"


def analyze_allergies(allergies, medicines):
    prompt = f"""
    You are an AI medical assistant.
    Check the following medicines against these allergies:

    Allergies: {allergies}
    Medicines: {medicines}

    Provide:
    - Whether each medicine is safe
    - Possible allergic reactions or warnings
    Answer in bullet points.
    """
    logging.info(f"Prompt to Gemini for allergy check: {prompt}")

    try:
        response = gemini_generate_with_retry(prompt)
        if response and hasattr(response, 'text'):
            text = response.text.strip()
            logging.info("Received response from Gemini for symptoms.")
            return format_markdown_response(text)
        else:
            logging.warning("❌ No text in AI response for symptoms.")
            return "❌ No response from AI."
    except Exception as e:
        logging.error(f"❌ Exception in get_symptom_recommendation: {str(e)}")
        return f"❌ Error: {str(e)}"
