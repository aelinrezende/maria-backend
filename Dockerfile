# Ultra-minimal Dockerfile for Mar.IA Backend
# Strategy: Install ALL deps in build including ML models (pre-downloaded via poetry)

# Build stage - Only basic dependencies
FROM python:3.13-slim as builder

# Set environment variables for minimal build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/app/.cache/huggingface

# Install MINIMAL system dependencies (no build tools!)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Install Poetry
RUN pip install --no-cache-dir "poetry==1.8.4"

# Set work directory
WORKDIR /app

# Create cache directory for Hugging Face models
RUN mkdir -p /app/.cache/huggingface

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install ALL dependencies including ML packages
RUN poetry install --no-interaction --no-ansi && \
    poetry cache clear --all pypi --no-interaction

# Copy and run model download script
COPY download_models.py ./
RUN python download_models.py && rm download_models.py

# Production stage - Ultra minimal
FROM python:3.13-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8080 \
    HF_HOME=/app/.cache/huggingface \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install ONLY runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash maria

# Set work directory
WORKDIR /app

# Create cache directory for models 
RUN mkdir -p /app/.cache/huggingface logs

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy cached models from builder stage
COPY --from=builder /app/.cache /app/.cache

# Copy application code
COPY src/ ./src/

# Change ownership to non-root user
RUN chown -R maria:maria /app

# Switch to non-root user
USER maria

# Expose port
EXPOSE 8080

# Health check (simple - don't require models)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start application directly (models pre-installed)
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]