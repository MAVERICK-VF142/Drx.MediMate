# No need to import genai directly here if model is passed
# from flask import current_app # Don't use current_app in services if possible

def get_drug_information(drug_name, gemini_model):
    if gemini_model is None: # <--- Add this check
        return "⚠️ AI features are not active (GEMINI_KEY missing). Cannot get drug information."

    prompt = (
        f"Provide a brief clinical summary for pharmacists on the drug {drug_name}:\n"
        "- Therapeutic uses\n"
        "- Standard dosage\n"
        "- Common & serious side effects\n"
        "- Contraindications\n"
        "- Important drug interactions\n"
        "Answer concisely in bullet points suitable for quick reference."
    )
    response = gemini_model.generate_content(prompt) # Use passed model
    return response.text.strip() if response and hasattr(response, 'text') else "❌ No response from AI."