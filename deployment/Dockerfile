FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r fednet && useradd -r -g fednet -d /app -s /sbin/nologin fednet

# Copy requirements first (Docker layer caching)
COPY requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p logs artifacts saved_models && \
    chown -R fednet:fednet /app

# Switch to non-root user
USER fednet

# Expose API/dashboard/inference ports (override with $PORT in platforms)
EXPOSE 5000 5001 5002

# Default: run dashboard via WSGI. Override with `APP_MODE=api|inference`.
ENV APP_MODE=dashboard

CMD ["bash", "-lc", "set -euo pipefail; PORT=${PORT:-5001}; case \"${APP_MODE}\" in dashboard) exec gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 --access-logfile - --error-logfile - ;; api) exec gunicorn api.app:app --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 --access-logfile - --error-logfile - ;; inference) export LOAD_INFERENCE_APP=true; exec gunicorn wsgi:inference_app --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 --access-logfile - --error-logfile - ;; *) echo \"Unknown APP_MODE=${APP_MODE} (expected: dashboard|api|inference)\" >&2; exit 2 ;; esac"]
