# Drug Side Effect Predictor

This module predicts possible side effects of a drug using a trained ML model.

## 🔍 How it works
- Input: Drug name
- Output: Predicted side effects with confidence scores

## 💡 Model Info
- Model: TF-IDF + OneVsRestClassifier (Logistic Regression)
- Trained on: Simulated drug-side effect dataset
- Output: Multi-label side effect predictions

## 🚀 How to Run
1. Install dependencies:
    pip install -r requirements.txt

2. Run the app:
    streamlit run app.py