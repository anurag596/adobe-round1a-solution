import os, json, joblib
import pandas as pd
from extract_headings import extract_line_objects

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"
MODEL_PATH = "/app/model/heading_model.pkl"

FEATURE_COLS = ["avg_size","text_length","num_prefix","is_bold","is_upper","above_body","darkness"]

def process_pdf(fname, clf):
    inp = os.path.join(INPUT_DIR, fname)
    out = os.path.join(OUTPUT_DIR, fname.replace(".pdf", ".json"))

    lines = extract_line_objects(inp, ocr_fallback=True)
    if not lines:
        print(f"⚠️No text in {fname}")
        return

    preds = []
    for l in lines:
        row = pd.DataFrame([{
            "avg_size":    l["avg_size"],
            "text_length": len(l["text"]),
            "num_prefix":  l["num_prefix"],
            "is_bold":     l["is_bold"],
            "is_upper":    1 if l["text"].isupper() else 0,
            "above_body":  1 if l["avg_size"] > 12 else 0,
            "darkness":    l.get("darkness", 0)
        }])[FEATURE_COLS]

        pred = clf.predict(row)[0] if clf else 1
        if pred == 1:
            if l["avg_size"] > 14:
                lvl = "H1"
            elif l["avg_size"] > 12:
                lvl = "H2"
            else:
                lvl = "H3"
            preds.append({"level": lvl, "text": l["text"], "page": l["page"]+1})

    result = {"title": os.path.splitext(fname)[0], "outline": preds}

    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {out} with {len(preds)} headings")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clf = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

    for fname in sorted(os.listdir(INPUT_DIR)):
        if fname.lower().endswith(".pdf"):
            process_pdf(fname, clf)

if __name__ == "__main__":
    main()
