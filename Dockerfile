# Ultra-minimal Dockerfile - Install dependencies with pip instead of Poetry
# Strategy: Use pip for direct installation to avoid Poetry overhead

FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers

# Install ONLY essential runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create user
RUN useradd --create-home --shell /bin/bash maria

# Set work directory
WORKDIR /app

# Create cache directories
RUN mkdir -p /app/.cache/transformers /app/.cache/sentence-transformers logs

# Install ONLY core dependencies with pip (not Poetry)
# Install basic FastAPI stack first
RUN pip install --no-cache-dir \
    fastapi==0.116.0 \
    uvicorn[standard]==0.23.0 \
    python-multipart==0.0.6 \
    pydantic==2.0.0 \
    sqlmodel==0.0.24 \
    asyncpg==0.29.0 \
    python-dotenv==1.0.0 \
    loguru==0.7.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.0 \
    pgvector==0.4.1 \
    wireup==2.0.0

# Copy application code
COPY src/ ./src/

# Copy Poetry files for potential runtime use (but don't install with Poetry)
COPY pyproject.toml poetry.lock ./

# Change ownership
RUN chown -R maria:maria /app

# Switch to non-root user
USER maria

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Startup script - install heavy dependencies at runtime
CMD ["sh", "-c", "
echo 'Installing additional dependencies...' && \
pip install --no-cache-dir \
    'sentence-transformers>=2.2.0,<3.0.0' \
    'anthropic[aiohttp]>=0.68.0,<0.69.0' \
    'google-genai>=0.8.0,<1.0.0' \
    'fastapi-restful[all]>=0.6.0,<0.7.0' \
    'fastapi-utils>=0.8.0,<0.9.0' \
    'httpx[http2]>=0.28.1,<0.29.0' \
    'numpy>=2.1.0,<2.3.0' \
    'pandas>=2.0.0,<3.0.0' \
    'alembic>=1.16.4,<2.0.0' \
    'markitdown[all]>=0.1.3,<0.2.0' \
    'pymupdf4llm>=0.0.27,<0.0.28' \
    'pymupdf>=1.26.4,<2.0.0' \
    'openai>=1.97.0,<2.0.0' \
    'pdfplumber>=0.11.7,<0.12.0' && \
echo 'Dependencies installed!' && \
python -c 'from src.backend.services.model_downloader import download_models; download_models()' && \
uvicorn src.backend.main:app --host 0.0.0.0 --port 8080
"]