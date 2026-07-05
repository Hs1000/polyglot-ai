FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV / EasyOCR runtime libs
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1 \
    # Compiler for native Python packages
    gcc g++ \
    # Unicode fonts for PDF export (covers Latin, Cyrillic, Greek, Arabic, Hebrew, etc.)
    fonts-dejavu-core \
    # TLS certs for HuggingFace model downloads
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so this layer is cached on code-only changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Persistent upload directory (overridden by a Docker volume in production)
RUN mkdir -p app/uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
