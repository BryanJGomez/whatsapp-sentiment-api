# Stage base: dependencias comunes
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage para App/API
FROM base AS app
EXPOSE 8080
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]

# Stage para Worker
FROM base AS worker
CMD ["python", "worker.py"]
