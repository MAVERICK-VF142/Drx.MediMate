from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import os
from flask import send_file
import io
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn import tree, svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# ---------------- Create Flask App ----------------
app = Flask(__name__)

# --------------- Load datasets & train models ---------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dis_sym_data = pd.read_csv(os.path.join(BASE_DIR, "Dataset/Original_Dataset.csv"))
doc_data = pd.read_csv(
    os.path.join(BASE_DIR, "Dataset/Doctor_Versus_Disease.csv"),
    encoding="latin1",
    names=["Disease", "Specialist"]
)
des_data = pd.read_csv(os.path.join(BASE_DIR, "Dataset/Disease_Description.csv"))

# Build one-hot symptom columns
columns_to_check = [col for col in dis_sym_data.columns if col != "Disease"]
symptoms_list = list(set(dis_sym_data.iloc[:, 1:].values.flatten()))
symptoms_list = [s for s in symptoms_list if pd.notna(s)]

for symptom in symptoms_list:
    dis_sym_data[symptom] = dis_sym_data.iloc[:, 1:].apply(
        lambda row: int(symptom in row.values), axis=1
    )

dis_sym_data_v1 = dis_sym_data.drop(columns=columns_to_check)
dis_sym_data_v1 = dis_sym_data_v1.loc[:, dis_sym_data_v1.columns.notna()]
dis_sym_data_v1.columns = dis_sym_data_v1.columns.str.strip()

# Encode labels
le = LabelEncoder()
dis_sym_data_v1["Disease"] = le.fit_transform(dis_sym_data_v1["Disease"])
X = dis_sym_data_v1.drop(columns="Disease")
y = dis_sym_data_v1["Disease"]

# Train models
algorithms = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": tree.DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
    "SVM": svm.SVC(probability=True),
    "NaiveBayes": GaussianNB(),
    "K-Nearest Neighbors": KNeighborsClassifier(),
}
for model in algorithms.values():
    model.fit(X, y)

_last_result_df = None  # store last results


# ------------------------------ Routes ------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    sorted_symptoms = sorted(symptoms_list, key=lambda s: str(s).lower())

    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptoms")
        threshold = int(request.form.get("threshold", 20))

        if not selected_symptoms:
            return render_template(
                "doctor_spec_index.html",
                symptoms=sorted_symptoms,
                error="⚠️ Please select at least one symptom!",
                default_threshold=threshold
            )

        test_data = {col: 1 if col in selected_symptoms else 0 for col in X.columns}
        test_df = pd.DataFrame(test_data, index=[0])

        predicted = []
        for model_name, model in algorithms.items():
            pred = model.predict(test_df)
            disease_label = le.inverse_transform(pred)[0]
            predicted.append(disease_label)

        disease_counts = Counter(predicted)
        percentage_per_disease = {
            disease: (count / len(algorithms)) * 100
            for disease, count in disease_counts.items()
        }

        percentage_per_disease = {
            d: p for d, p in percentage_per_disease.items() if p >= threshold
        }

        if len(percentage_per_disease) == 0:
            return render_template(
                "doctor_spec_index.html",
                symptoms=sorted_symptoms,
                error="❌ No diseases met the confidence threshold!",
                default_threshold=threshold
            )

        result_df = pd.DataFrame({
            "Disease": list(percentage_per_disease.keys()),
            "Chances (%)": list(percentage_per_disease.values())
        })
        result_df = result_df.merge(doc_data, on="Disease", how="left")
        result_df = result_df.merge(des_data, on="Disease", how="left")

        global _last_result_df
        _last_result_df = result_df.copy()

        chart_labels = result_df["Disease"].tolist()
        chart_values = np.round(result_df["Chances (%)"].astype(float), 2).tolist()

        return render_template(
            "doctor_spec_result.html",
            results=result_df.to_dict(orient="records"),
            symptoms_selected=selected_symptoms,
            threshold=threshold,
            chart_labels=chart_labels,
            chart_values=chart_values
        )

    return render_template(
        "doctor_spec_index.html",
        symptoms=sorted_symptoms,
        default_threshold=20
    )

@app.route("/download_csv")
def download_csv():
    global _last_result_df
    if _last_result_df is None:
        return "No results available. Run a prediction first.", 400

    # Save DataFrame to CSV in memory
    csv_buffer = io.StringIO()
    _last_result_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="predicted_diseases.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)
