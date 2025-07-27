# # src/generate_training_data.py
# import csv
# from pathlib import Path
# from extract_headings import extract_fonts_from_pdf
# import numpy as np

# INPUT_DIR = Path("/app/input")
# OUTPUT_DIR = Path("/app/output")

# def process_pdf(pdf_path):
#     font_stats = extract_fonts_from_pdf(pdf_path)
#     if not font_stats:
#         print(f"⚠️ No text in {pdf_path.name}")
#         return

#     sizes = [size for _, size, _ in font_stats]
#     body_median = np.median(sizes) if sizes else 12.0

#     out_csv = OUTPUT_DIR / f"training_data_{pdf_path.stem}.csv"
#     with open(out_csv, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["text", "avg_size", "text_length", "num_prefix", "is_bold", "is_upper", "above_body", "label"])

#         for page, size, text in font_stats:
#             stripped = text.strip()
#             if not stripped:
#                 continue
#             num_prefix = 1 if stripped[0].isdigit() else 0
#             is_bold = 0  # pdfminer doesn't easily expose bold, can extend later
#             is_upper = 1 if stripped.isupper() else 0
#             above_body = 1 if size > body_median else 0

#             writer.writerow([stripped, size, len(stripped), num_prefix, is_bold, is_upper, above_body, ""])

#     print(f"✅ Generated {out_csv.name}")

# def main():
#     OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
#     pdfs = list(INPUT_DIR.glob("*.pdf"))
#     for pdf in pdfs:
#         process_pdf(pdf)

# if __name__ == "__main__":
#     main()













# src/generate_training_data.py
# import csv, re, json
# from pathlib import Path
# from extract_headings import extract_line_objects, NUM_PREFIX_RE
# import numpy as np

# INPUT_DIR = Path("/app/input")
# OUTPUT_DIR = Path("/app/output")

# def process_pdf(pdf_path):
#     # Corresponding JSON file with labeled headings
#     json_path = OUTPUT_DIR / f"{pdf_path.stem}.json"
#     out_csv = OUTPUT_DIR / f"training_data_{pdf_path.stem}.csv"

#     if not json_path.exists():
#         print(f"⚠️ Skipping {pdf_path.name}, no {json_path.name}")
#         return

#     # Load known headings from JSON
#     with open(json_path, encoding="utf-8") as f:
#         labeled = json.load(f)
#     known_headings = {h["text"].strip().lower() for h in labeled.get("outline", [])}

#     # Extract lines
#     lines = extract_line_objects(pdf_path, ocr_fallback=False)
#     if not lines:
#         print(f"⚠️ No text in {pdf_path.name}")
#         return

#     sizes = [l["avg_size"] for l in lines]
#     body_median = np.median(sizes)

#     with open(out_csv, "w", newline='', encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             "text","avg_size","text_length","num_prefix",
#             "is_bold","is_upper","above_body","col","label"
#         ])

#         # Sort reading order: page, column, y (top→bottom)
#         lines.sort(key=lambda l: (l["page"], l["col"], -l["y1"]))

#         for l in lines:
#             txt = l["text"].strip()
#             if not txt:
#                 continue
#             num_prefix = 1 if NUM_PREFIX_RE.match(txt) else 0
#             is_upper = 1 if txt.isupper() else 0
#             above_body = 1 if l["avg_size"] > body_median else 0
#             is_bold = l.get("is_bold", 0)

#             # 🔹 Auto-label from JSON
#             label = 1 if txt.lower() in known_headings else 0

#             writer.writerow([
#                 txt, l["avg_size"], len(txt),
#                 num_prefix, is_bold, is_upper,
#                 above_body, l["col"], label
#             ])

#     print(f"✅ Generated {out_csv.name} ({len(lines)} rows)")

# def main():
#     OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
#     for pdf in INPUT_DIR.glob("*.pdf"):
#         process_pdf(pdf)

# if __name__ == "__main__":
#     main()













# src/generate_training_data.py
import csv, re
from pathlib import Path
from extract_headings import extract_line_objects, NUM_PREFIX_RE
import numpy as np

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

def process_pdf(pdf_path):
    lines = extract_line_objects(pdf_path, ocr_fallback=False)
    if not lines:
        print(f"⚠️ No text in {pdf_path.name}")
        return

    sizes = [l["avg_size"] for l in lines]
    body_median = np.median(sizes)

    out_csv = OUTPUT_DIR / f"training_data_{pdf_path.stem}.csv"
    with open(out_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "text","avg_size","text_length","num_prefix",
            "is_bold","is_upper","above_body","col","darkness","label"
        ])

        for l in lines:
            txt = l["text"].strip()
            if not txt:
                continue
            num_prefix = 1 if NUM_PREFIX_RE.match(txt) else 0
            is_upper = 1 if txt.isupper() else 0
            above_body = 1 if l["avg_size"] > body_median else 0

            # Skip very light watermarks (optional)
            if l["darkness"] < 0.2:
                continue

            writer.writerow([
                txt, l["avg_size"], len(txt), num_prefix,
                l["is_bold"], is_upper, above_body, l["col"],
                l.get("score", 0), 0  # <-- default label = 0
            ])


    print(f"✅ Generated {out_csv.name} ({len(lines)} rows)")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    for pdf in INPUT_DIR.glob("*.pdf"):
        process_pdf(pdf)

if __name__ == "__main__":
    main()
