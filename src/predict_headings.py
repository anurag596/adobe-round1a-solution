# src/predict_headings.py
import pandas as pd
import joblib
import json
from pathlib import Path

MODEL = Path("/app/model/heading_model.pkl")
DATA = Path("/app/data/training_data.csv")
OUT = Path("/app/output/predicted.json")

model = joblib.load(MODEL)
df = pd.read_csv(DATA)
features = df[["avg_size", "text_length", "num_prefix", "is_bold", "is_upper", "above_body"]]
df["prediction"] = model.predict(features)

result = []
for _, row in df.iterrows():
    if row["prediction"] == 1:
        result.append({"text": row["text"], "font_size": row["avg_size"]})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"✅ Predictions saved to {OUT}")
