


import streamlit as st
import pandas as pd
import os
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn import tree, svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# Streamlit page config
st.set_page_config(page_title="Disease Predictor", page_icon="🩺", layout="wide")

# CSS styling
st.markdown("""
    <style>
    .stApp { background: #f9f9f9; }
    .stButton>button {
        background: #4CAF50;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover { background: #45a049; }
    </style>
""", unsafe_allow_html=True)

# Get base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load datasets
dis_sym_data = pd.read_csv(os.path.join(BASE_DIR, "Original_Dataset.csv"))
doc_data = pd.read_csv(os.path.join(BASE_DIR, "Doctor_Versus_Disease.csv"), encoding='latin1', names=['Disease', 'Specialist'])
des_data = pd.read_csv(os.path.join(BASE_DIR, "Disease_Description.csv"))

# Prepare symptom columns
columns_to_check = [col for col in dis_sym_data.columns if col != 'Disease']
symptoms_list = list(set(dis_sym_data.iloc[:, 1:].values.flatten()))
symptoms_list = [s for s in symptoms_list if pd.notna(s)]

for symptom in symptoms_list:
    dis_sym_data[symptom] = dis_sym_data.iloc[:, 1:].apply(lambda row: int(symptom in row.values), axis=1)

dis_sym_data_v1 = dis_sym_data.drop(columns=columns_to_check)
dis_sym_data_v1 = dis_sym_data_v1.loc[:, dis_sym_data_v1.columns.notna()]
dis_sym_data_v1.columns = dis_sym_data_v1.columns.str.strip()

# Encode labels
le = LabelEncoder()
dis_sym_data_v1['Disease'] = le.fit_transform(dis_sym_data_v1['Disease'])
X = dis_sym_data_v1.drop(columns="Disease")
y = dis_sym_data_v1['Disease']

# Train models
algorithms = {
    'Logistic Regression': LogisticRegression(),
    'Decision Tree': tree.DecisionTreeClassifier(),
    'Random Forest': RandomForestClassifier(),
    'SVM': svm.SVC(probability=True),
    'NaiveBayes': GaussianNB(),
    'K-Nearest Neighbors': KNeighborsClassifier(),
}
for model in algorithms.values():
    model.fit(X, y)

# Sidebar for inputs
st.sidebar.header("🛠️ Input Options")
selected_symptoms = st.sidebar.multiselect("🔍 Search & Select Symptoms", symptoms_list)
threshold = st.sidebar.slider("📊 Confidence threshold (%)", 0, 100, 20)
show_chart = st.sidebar.checkbox("📈 Show Probability Chart", value=True)

# Main title
st.markdown("<h1 style='text-align: center;'>🩺 Disease Predictor & Doctor Specialist Recommender</h1>", unsafe_allow_html=True)

# Prediction button
if st.sidebar.button("🔎 Predict Disease"):
    if len(selected_symptoms) == 0:
        st.warning("⚠️ Please select at least one symptom!")
    else:
        with st.spinner("⏳ Analyzing symptoms and predicting..."):
            # Prepare test data
            test_data = {col: 1 if col in selected_symptoms else 0 for col in X.columns}
            test_df = pd.DataFrame(test_data, index=[0])

            predicted = []
            for model_name, model in algorithms.items():
                pred = model.predict(test_df)
                disease = le.inverse_transform(pred)[0]
                predicted.append(disease)

            disease_counts = Counter(predicted)
            percentage_per_disease = {
                disease: (count / len(algorithms)) * 100 for disease, count in disease_counts.items()
            }

            # Apply threshold filter
            percentage_per_disease = {d: p for d, p in percentage_per_disease.items() if p >= threshold}

            if len(percentage_per_disease) == 0:
                st.error("❌ No diseases met the confidence threshold!")
            else:
                result_df = pd.DataFrame({
                    "Disease": list(percentage_per_disease.keys()),
                    "Chances (%)": list(percentage_per_disease.values())
                })
                result_df = result_df.merge(doc_data, on='Disease', how='left')
                result_df = result_df.merge(des_data, on='Disease', how='left')

                st.subheader("📋 Prediction Results")
                st.dataframe(result_df, use_container_width=True)

                # Download button first
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="disease_predictions.csv",
                    mime="text/csv"
                )

                # Show chart after the download button if enabled
                if show_chart:
                    st.subheader("📊 Probability Chart")
                    st.bar_chart(result_df.set_index("Disease")["Chances (%)"])
