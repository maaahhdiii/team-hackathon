# ─────────────────────────────────────────────────
#  VulnLab — Deliberately Vulnerable Web App
#  For cybersecurity training purposes only.
# ─────────────────────────────────────────────────
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/app.py ./app.py

# Copy frontend files into a static subfolder
COPY frontend/ ./static/

# Flask will serve the frontend as static files
ENV FLASK_APP=app.py
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

# Initialise DB then start server
CMD ["python", "app.py"]
