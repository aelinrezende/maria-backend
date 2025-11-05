#!/usr/bin/env python3
"""
Script to pre-download ML models during Docker build.
This ensures models are cached in the image and don't need to be downloaded at runtime.
"""

import os
from sentence_transformers import SentenceTransformer

cache_dir = os.getenv("HF_HOME", "/app/.cache/huggingface")
model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

print(f"Downloading models to: {cache_dir}")
print(f"Downloading model: {model_name}")

try:
    model = SentenceTransformer(model_name, cache_folder=cache_dir)
    print(f"✓ Model {model_name} downloaded successfully")
    print(f"✓ Model size: {model.get_max_seq_length()} max tokens")
    print(f"✓ Embedding dimension: {model.get_sentence_embedding_dimension()}")
except Exception as e:
    print(f"✗ Error downloading model: {e}")
    raise

print("\n✓ All models downloaded successfully!")
