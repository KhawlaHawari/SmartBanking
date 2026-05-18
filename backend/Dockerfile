FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN grep -v "pywin32" requirements.txt > requirements_linux.txt && \
    pip install --no-cache-dir -r requirements_linux.txt

COPY . .

RUN mkdir -p /app/data /app/saved_models /app/mlruns

ENV API_HOST=0.0.0.0
ENV API_PORT=8023

EXPOSE 8023

CMD ["sh", "-c", "uvicorn app.main:app --host ${API_HOST} --port ${API_PORT}"]