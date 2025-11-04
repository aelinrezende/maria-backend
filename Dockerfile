# Multi-stage Dockerfile for Mar.IA Backend on Google Cloud Run
# Optimized for Python 3.13, Poetry, and ML dependencies

# Build stage - Installs dependencies
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for pgvector and ML models
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Install Poetry
RUN pip install "poetry==1.8.4"

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create venv in the container
RUN poetry config virtualenvs.create false

# Install only production dependencies to save space
RUN poetry install --only=main --no-interaction --no-ansi && \
    poetry cache clear --all pypi --no-interaction

# Production stage - Minimal runtime image
FROM python:3.13-slim as production

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8080

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash maria

# Set work directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Change ownership to non-root user
RUN chown -R maria:maria /app

# Switch to non-root user
USER maria

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]