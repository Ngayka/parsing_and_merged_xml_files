FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tasks.py celery_app.py .

RUN mkdir -p /data/feeds

CMD ["bash", "-c", "sleep infinity"]
