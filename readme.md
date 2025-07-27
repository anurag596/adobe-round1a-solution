# Adobe India Hackathon Round 1A: PDF Heading Extractor

## Overview
This project extracts structured outlines (Title, H1, H2, H3) from PDFs using a hybrid rules + ML approach, with multilingual OCR support and multi‑column layout handling.

## Approach
1. **Text Extraction**  
   - Use [PyMuPDF](https://pymupdf.readthedocs.io/) to parse pages and spans.  
2. **OCR Fallback**  
   - Install `tesseract-ocr` in Docker; use `pytesseract` when vector text is missing.  
3. **Feature Extraction**  
   - Per line: `avg_size`, `text_length`, `num_prefix`, `is_bold`, `is_upper`, `above_body`, `darkness`, `col`.  
4. **Training Pipeline**  
   - Generate per-PDF CSVs via `generate_training_data.py`.  
   - Merge them with `merge_csvs.py`.  
   - Train a `LogisticRegression` model on locked-in `FEATURE_COLS` in `train_heading_model.py`.  
5. **Inference**  
   - `main.py` loads `heading_model.pkl`, extracts lines, builds a pandas DataFrame with the same feature columns, predicts headings, and assigns H1/H2/H3 by font-size thresholds.

## Docker Setup
- **Base Image**: `python:3.10-slim` (linux/amd64)  
- **Installs**: PyMuPDF, pdfminer.six, pandas, scikit-learn, pytesseract + `tesseract-ocr`, joblib  
- **Offline**: No internet at runtime  
- **Model Size**: < 200 MB

### Build & Run (Inference Only)
```bash
# Build AMD64-compatible image
docker build --platform linux/amd64 -t pdf-heading-extractor:latest .

# Run inference (reads PDFs from ./input, writes JSON to ./output)
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/model:/app/model" \
  -v "$(pwd)/output:/app/output" \
  pdf-heading-extractor:latest
