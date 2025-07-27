import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

# Lock in the same features as main.py
FEATURE_COLS = ["avg_size","text_length","num_prefix","is_bold","is_upper","above_body","darkness"]

# Load training data
df = pd.read_csv("data/training_data.csv")

# Safety check
missing = [c for c in FEATURE_COLS if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

X = df[FEATURE_COLS]
y = df["label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=500)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
Path("model").mkdir(exist_ok=True)
joblib.dump(model, "model/heading_model.pkl")
print("✅ Model saved to model/heading_model.pkl")
