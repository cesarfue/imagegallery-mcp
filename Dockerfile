FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY gallery .
COPY results .
COPY chroma_db .

RUN useradd -m -u 1000 mcpuser && \
  chown -R mcpuser:mcpuser /app

USER mcpuser

CMD ["python", "server.py"]
