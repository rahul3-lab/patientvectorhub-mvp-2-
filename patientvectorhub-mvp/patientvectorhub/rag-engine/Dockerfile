FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY rag-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag-engine/ .
COPY vector-store/app ./vector_store_pkg

EXPOSE 8002
CMD ["uvicorn", "app.pipeline:app", "--host", "0.0.0.0", "--port", "8002"]
