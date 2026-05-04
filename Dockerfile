# syntax=docker/dockerfile:1
# ---- Base image ----
FROM python:3.11-slim

WORKDIR /app

# Install build tools needed for some Python packages (e.g. scikit-learn wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies ----
# Copy only requirements first so Docker can cache this layer.
COPY backend/requirements.txt ./requirements.txt

# Install CPU-only PyTorch first (much smaller than the default CUDA build),
# then install the rest of the requirements.
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# ---- Application code ----
COPY backend/ ./backend/
COPY models/  ./models/
COPY data/  ./data/

# ---- Runtime ----
# Railway injects $PORT at runtime. Default to 8000 for local docker runs.
ENV PORT=8000

# Use shell form so $PORT is expanded at runtime.
CMD uvicorn backend.src.app:app --host 0.0.0.0 --port $PORT
