# ─── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:22-alpine AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ─── Stage 2: Production image ────────────────────────────────────────────────
FROM python:3.12-slim

# System packages: nginx, supervisor, LibreOffice (for .xlsb → .ods conversion)
# libreoffice-calc pulls in libreoffice-core and libreoffice-common
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    libreoffice-calc \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (own layer for cache efficiency)
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source code
COPY backend/ .

# Built React SPA from Stage 1
COPY --from=frontend-build /build/dist /app/frontend/dist

# Nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/masms
RUN rm -f /etc/nginx/sites-enabled/default \
    && ln -sf /etc/nginx/sites-available/masms /etc/nginx/sites-enabled/masms

# Supervisord configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/masms.conf

# Data directory (will be overridden by volume mount)
RUN mkdir -p /app/backend/data /var/log/supervisor

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
