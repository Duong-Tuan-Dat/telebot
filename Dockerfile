FROM python:3.11-slim

# Cài Tesseract + ngôn ngữ tiếng Việt
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tesseract-ocr tesseract-ocr-vie libgl1 \
 && rm -rf /var/lib/apt/lists/*

# Thư mục làm việc
WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Chạy app
CMD ["python", "main.py"]
