# Use a lightweight Python base image
FROM python:3.12-slim

# Ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (build essentials for any wheels that may need compiling)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly (no requirements.txt present)
RUN pip install --no-cache-dir \
      fastapi \
      "uvicorn[standard]" \
      SQLAlchemy \
      python-dotenv \
      twilio \
      psycopg2-binary

# Copy application code
COPY . /app

# Expose FastAPI default port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


