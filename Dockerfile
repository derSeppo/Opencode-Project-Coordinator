# OpenCode AI Coordinator Dockerfile
# Multi-stage build for production and development

# ============================================================================
# Stage 1: Base image with dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# ============================================================================
# Stage 2: Build stage
# ============================================================================
FROM base as builder

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN poetry export -f requirements.txt --output requirements-lock.txt --without-hashes && \
    pip install --user -r requirements-lock.txt && \
    rm requirements-lock.txt

# ============================================================================
# Stage 3: Production image
# ============================================================================
FROM base as production

# Copy installed dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY open_coordinator/ ./open_coordinator/
COPY main.py .
COPY .env .

# Set ownership
RUN chown -R appuser:appuser /home/appuser/app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5).raise_for_status()" || exit 1

# Set default command
ENTRYPOINT ["python", "main.py"]
CMD ["--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Development image (optional)
# ============================================================================
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy all files
COPY . .

# Install all dependencies (including dev)
RUN poetry install

# Set ownership
RUN chown -R appuser:appuser /home/appuser/app

# Switch to app user
USER appuser

# Expose port
EXPOSE 8000

# Set default command for development (with auto-reload)
ENTRYPOINT ["python", "main.py"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--reload", "--debug"]
