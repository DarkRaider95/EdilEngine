FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for sentence-transformers (torch needs libgomp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# sentence-transformers pulls torch (~800MB), this takes a while on first build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Copy seed script for data loading
COPY seed.py /app/seed.py

# Create directory for caching sentence-transformers models
RUN mkdir -p /app/.cache/huggingface
ENV HF_HOME=/app/.cache/huggingface

# Expose port (Cloud Run default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]