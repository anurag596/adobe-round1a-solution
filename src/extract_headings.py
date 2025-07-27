import fitz
import numpy as np
import re
from PIL import Image
import pytesseract

NUM_PREFIX_RE = re.compile(r"^(\d+\.)+\s*")
OCR_LANGS = "eng+hin+jpn+chi_sim"

def extract_line_objects(pdf_path, ocr_fallback=True):
    doc = fitz.open(pdf_path)
    all_lines = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b["type"] != 0:
                continue
            for line in b["lines"]:
                spans = line["spans"]
                sizes = [span["size"] for span in spans]
                text = "".join(span["text"] for span in spans).strip()

                #Calculating Color/Darkness
                colors = [span.get("color", (0,0,0)) for span in spans]
                if colors and isinstance(colors[0], tuple):
                    brightness = np.mean([np.mean(c) for c in colors])
                else:
                    rgb_vals = [((c>>16)&255, (c>>8)&255, c&255) for c in colors]
                    brightness = np.mean([np.mean(c)/255 for c in rgb_vals])

                darkness = 1 - brightness  # closer to 1 = dark text, closer to 0 = light

                # OCR fallback if no text
                if not text and ocr_fallback:
                    x0 = min(s["bbox"][0] for s in spans)
                    y0 = min(s["bbox"][1] for s in spans)
                    x1 = max(s["bbox"][2] for s in spans)
                    y1 = max(s["bbox"][3] for s in spans)
                    clip = page.get_pixmap(clip=fitz.Rect(x0, y0, x1, y1))
                    img = Image.frombytes("RGB", [clip.width, clip.height], clip.samples)
                    text = pytesseract.image_to_string(img, lang=OCR_LANGS).strip()
                    sizes = [12.0]
                    darkness = 1.0  # assume dark if OCR

                if not text:
                    continue

                x0 = min(span["bbox"][0] for span in spans)
                y0 = min(span["bbox"][1] for span in spans)
                y1 = max(span["bbox"][3] for span in spans)
                avg_size = float(np.mean(sizes))
                bold = any("Bold" in span["font"] for span in spans)
                num_prefix = bool(NUM_PREFIX_RE.match(text))

                all_lines.append({
                    "page": page_num,
                    "text": text,
                    "x0": x0,
                    "y0": y0,
                    "y1": y1,
                    "avg_size": avg_size,
                    "is_bold": 1 if bold else 0,
                    "num_prefix": 1 if num_prefix else 0,
                    "darkness": round(darkness, 3)
                })

    out = []
    for page_num in set(l["page"] for l in all_lines):
        page_lines = [l for l in all_lines if l["page"] == page_num]
        x_vals = [l["x0"] for l in page_lines]
        if max(x_vals)-min(x_vals) > 100:
            median_x = np.median(x_vals)
            for l in page_lines:
                l["col"] = 0 if l["x0"] <= median_x else 1
        else:
            for l in page_lines:
                l["col"] = 0
        out.extend(page_lines)

    return out
