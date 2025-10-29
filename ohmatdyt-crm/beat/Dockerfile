FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from API directory
COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from API directory
RUN mkdir -p /app/app
COPY ./api/app /app/app

COPY ./beat/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /var/app/media /var/app/static

ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "app.celery_app:celery", "beat", "--loglevel=info"]