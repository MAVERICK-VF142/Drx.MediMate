import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

df = pd.read_csv("drugs_side_effects.csv")

# Keep only drug name and side effects
df = df[['drug_name', 'side_effects']].dropna()

df['side_effects'] = df['side_effects'].apply(lambda x: [s.strip() for s in x.split(',')])

all_se = df['side_effects'].explode()
top_effects = all_se.value_counts().nlargest(50).index
df['side_effects'] = df['side_effects'].apply(lambda effects: [e for e in effects if e in top_effects])
df = df[df['side_effects'].map(len) > 0]

mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['side_effects'])

X_train, X_test, y_train, y_test = train_test_split(
    df['drug_name'], y, test_size=0.2, random_state=42
)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', OneVsRestClassifier(LogisticRegression(solver='liblinear')))
])
pipeline.fit(X_train, y_train)

score = pipeline.score(X_test, y_test)
print(f"Accuracy: {score:.2f}")

with open('ml/side_effect_model.pkl', 'wb') as f:
    pickle.dump(pipeline, f)
with open('ml/mlb.pkl', 'wb') as f:
    pickle.dump(mlb, f)

print("Trained model saved successfully!")
