# ---- Stage 1: Frontend build ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --prefer-offline
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Backend ----
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/dist ./backend/frontend_dist/

WORKDIR /app/backend

# collectstatic은 빌드 타임에 실행 (dummy DB 사용)
RUN DJANGO_SETTINGS_MODULE=meetup_backend.settings_production \
    SECRET_KEY=placeholder-for-collectstatic \
    DATABASE_URL=sqlite:////tmp/placeholder.db \
    python manage.py collectstatic --noinput

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=meetup_backend.settings_production

CMD ["sh", "-c", "gunicorn meetup_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --log-level info"]
