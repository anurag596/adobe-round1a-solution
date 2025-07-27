FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# Install Tesseract + language packs
RUN apt-get update && \
    apt-get install -y \
      tesseract-ocr \  
      tesseract-ocr-hin \  
      tesseract-ocr-jpn \  
      tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

CMD ["python", "src/main.py"]
