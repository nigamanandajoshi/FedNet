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
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p logs artifacts saved_models && \
    chown -R fednet:fednet /app

# Switch to non-root user
USER fednet

# Expose API and dashboard ports
EXPOSE 5000 5001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run with gunicorn (production WSGI server)
CMD ["gunicorn", "wsgi:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
