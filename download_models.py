#!/usr/bin/env python3
"""
Script to pre-download ML models during Docker build.
This ensures models are cached in the image and don't need to be downloaded at runtime.
Uses HuggingFace token to avoid IP blocks.
"""

import os
from huggingface_hub import login
from sentence_transformers import SentenceTransformer

# Login to HuggingFace if token is provided
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    print("Authenticating with HuggingFace...")
    login(token=hf_token)
    print("✓ Authenticated successfully")
else:
    print("⚠ No HF_TOKEN provided, downloading without authentication")

cache_dir = os.getenv("HF_HOME", "/models")
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
