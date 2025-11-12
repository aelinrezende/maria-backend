# Dockerfile Multi-stage Ultra-otimizado para Backend Mar.IA
# Estratégia: Isolar download de modelo, build Python e runtime mínimo

# =============================================================================
# ESTÁGIO 1: Downloader de Modelos (isolado para maximizar eficiência de espaço)
# =============================================================================
FROM python:3.13-slim AS model-downloader

# Ambiente para download - consistente com runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/app/.cache/huggingface

# Instalar APENAS dependências essenciais do sistema para download
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Instalar Rust para compilação do tokenizers
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    rustc --version && \
    cargo --version

# Garantir que o PATH do Rust esteja disponível em todos os RUNs subsequentes
ENV PATH="/root/.cargo/bin:$PATH"

# Instalar Poetry para gerenciamento de dependências
RUN pip install --no-cache-dir "poetry==1.8.4"

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos Poetry para gerenciamento consistente de dependências
COPY pyproject.toml poetry.lock* ./

# Configurar Poetry
RUN poetry config virtualenvs.create false

# Instalar APENAS dependências de modelo do pyproject.toml
RUN poetry install --only model --no-interaction --no-ansi && \
    poetry cache clear --all pypi --no-interaction

# Criar diretório de cache
RUN mkdir -p /app/.cache/huggingface

# Argumentos de build para o download do modelo
ARG HF_TOKEN
ARG EMBEDDING_MODEL

# Copiar e usar script de download existente
COPY download_models.py ./

# Baixar modelo para local de cache consistente
ENV HF_TOKEN=${HF_TOKEN}
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}
RUN python download_models.py && \
    echo "✅ Modelo baixado com sucesso" && \
    du -sh /app/.cache/huggingface

# =============================================================================
# ESTÁGIO 2: Builder Python (apenas dependências)
# =============================================================================
FROM python:3.13-slim AS python-builder

# Ambiente para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Instalar Poetry
RUN pip install --no-cache-dir "poetry==1.8.4"

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos poetry para gerenciamento consistente de dependências
COPY pyproject.toml poetry.lock* ./

# Configure Poetry for production
RUN poetry config virtualenvs.create false

# Install dependencies WITHOUT dev dependencies
RUN poetry install --only main --no-interaction --no-ansi && \
    poetry cache clear --all pypi --no-interaction && \
    (pip cache purge 2>/dev/null || echo "pip cache already disabled")

# =============================================================================
# STAGE 3: Production Runtime (ultra-minimal)
# =============================================================================
FROM python:3.13-slim AS production

# Production environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8080 \
    HF_HOME=/app/.cache/huggingface \
    PYTHONPATH="/app/src"

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

# Create cache directory with proper permissions
RUN mkdir -p /app/.cache/huggingface /app/logs && \
    chown -R maria:maria /app

# Copy installed Python packages from builder stage
COPY --from=python-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy downloaded models from model-downloader stage
COPY --from=model-downloader /app/.cache/huggingface /app/.cache/huggingface

# Copy application code
COPY --chown=maria:maria src/ ./src/

# Switch to non-root user
USER maria

# Expose port
EXPOSE 8080

# Health check with standard startup time (models already downloaded)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start application (models are pre-downloaded during build)
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--http2"]