import streamlit as st
import pickle
import numpy as np

with open("ml/side_effect_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("ml/mlb.pkl", "rb") as f:
    mlb = pickle.load(f)

# App UI
st.set_page_config(page_title="Drug Side Effect Predictor", layout="centered")
st.title("💊 Drug Side Effect Predictor")
st.write("Enter a drug name to predict possible side effects using a trained ML model.")

drug_input = st.text_input("Enter Drug Name", placeholder="e.g., Ibuprofen")

# Predict
if st.button("Predict Side Effects"):
    if drug_input.strip() == "":
        st.warning("Please enter a valid drug name.")
    else:
        try:
            # Get prediction probabilities
            proba = model.predict_proba([drug_input])[0]
            side_effects = mlb.classes_

            # Combine predictions with side effects
            predictions = list(zip(side_effects, proba))

            # Filter those with probability > 0.2 (threshold)
            filtered_preds = [p for p in predictions if p[1] > 0.2]

            if filtered_preds:
                st.success(f"Predicted side effects for **{drug_input.title()}**:")
                for effect, prob in sorted(filtered_preds, key=lambda x: x[1], reverse=True):
                    st.markdown(f"- **{effect}**: `{prob:.2f}`")
            else:
                st.info("No significant side effects found with high confidence.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
