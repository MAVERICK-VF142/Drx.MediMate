# from flask import current_app

def get_symptom_recommendation(symptoms, gemini_model):
    if gemini_model is None:
        return "⚠️ AI features are not active (GEMINI_KEY missing). Cannot provide symptom recommendations."
    
    prompt = (
        f"Given the symptoms: {symptoms}, recommend over-the-counter treatment options."
        " List common side effects, important interactions, and safety tips. "
        " If symptoms suggest a medical emergency or severe condition, recommend immediate doctor consultation. "
        "Respond concisely in bullet points without disclaimers."
    )
    response = gemini_model.generate_content(prompt) # Use passed model
    return response.text.strip() if response and hasattr(response, 'text') else "❌ No response from AI."