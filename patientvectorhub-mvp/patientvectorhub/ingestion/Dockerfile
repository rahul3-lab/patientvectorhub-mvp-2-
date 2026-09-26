FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingestion/ .
COPY vector-store/app ./vector_store_pkg

EXPOSE 8001
CMD ["uvicorn", "app.worker:app", "--host", "0.0.0.0", "--port", "8001"]
