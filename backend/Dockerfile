# ======================================================
# 🧠 Workmate OS Backend - FastAPI + Uvicorn
# ======================================================

# ---- Base image ----
FROM python:3.12-slim AS base

# ---- Environment ----
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# ---- Arbeitsverzeichnis ----
WORKDIR /app

# ---- Systemabhängigkeiten ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Abhängigkeiten kopieren ----
COPY requirements.txt .

# ---- Pakete installieren ----
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- App-Code kopieren ----
COPY ./app ./app

# ---- Default CMD (für Dev via Compose überschrieben) ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
