"""
Lazy model downloader - downloads ML models only when needed
This reduces Docker build size significantly
"""

import os
from loguru import logger


def download_models():
    """Download ML models lazily at startup"""

    # Set cache directories to persistent volume
    os.environ["TRANSFORMERS_CACHE"] = "/app/.cache/transformers"
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/app/.cache/sentence-transformers"

    logger.info("Starting lazy model download...")

    try:
        # Import sentence transformers (this will trigger download)
        from sentence_transformers import SentenceTransformer

        # Download the embedding model (this is the heavy one ~1.5GB)
        logger.info("Downloading embedding model: intfloat/multilingual-e5-base")
        model = SentenceTransformer('intfloat/multilingual-e5-base')
        logger.info("Embedding model downloaded successfully!")

        # Test the model to ensure it's working
        test_embedding = model.encode("test", normalize_embeddings=True)
        logger.info(f"Model test successful - embedding shape: {test_embedding.shape}")

    except Exception as e:
        logger.error(f"Failed to download models: {e}")
        # Don't fail the startup - models can be downloaded later
        logger.warning("Application will continue - models will be downloaded on first use")

    logger.info("Model download process completed!")