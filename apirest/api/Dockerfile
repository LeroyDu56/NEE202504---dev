# ---- Étape builder ----
  FROM python:3.11-slim AS builder
  WORKDIR /app
  
  # Installer dépendances système
  RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc build-essential python3-dev libffi-dev libssl-dev default-libmysqlclient-dev pkg-config libxml2-dev libxslt1-dev \
      && rm -rf /var/lib/apt/lists/*
  
  COPY . ./api
  
  ENV PATH=/root/.local/bin:$PATH
  ENV PYTHONPATH=/app/api
  
  RUN pip install --user --no-cache-dir -r api/requirements.txt
  
  # ---- Étape runtime ----
  FROM python:3.11-slim
  WORKDIR /app
  
  COPY --from=builder /root/.local /root/.local
  COPY . ./api
  
  ENV PATH=/root/.local/bin:$PATH
  ENV PYTHONPATH=/app/api
  
  EXPOSE 8000
  
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  