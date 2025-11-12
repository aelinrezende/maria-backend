#!/usr/bin/env python3
"""
Optimized script for model downloading in multi-stage Docker builds.
Checks if models already exist in cache before attempting download.
Includes space monitoring and cleanup functionality.
"""

import os
import shutil
from huggingface_hub import login
from sentence_transformers import SentenceTransformer

def get_disk_space(path: str = "/") -> tuple[int, int]:
    """Get available and total disk space in MB."""
    stat = shutil.disk_usage(path)
    return stat.free // (1024 * 1024), stat.total // (1024 * 1024)



def main():
    # Environment variables
    hf_token = os.getenv("HF_TOKEN")
    cache_dir = os.getenv("HF_HOME")
    model_name = os.getenv("EMBEDDING_MODEL")

    print("🤖 Mar.IA Model Downloader")
    print(f"📁 Cache directory: {cache_dir}")
    print(f"🎯 Target model: {model_name}")

    # Check disk space
    free_mb, total_mb = get_disk_space()

    print(f"💾 Available disk space: {free_mb:,} MB / {total_mb:,} MB")

    if free_mb < 2048:  # Less than 2GB free
        print(f"⚠️  WARNING: Low disk space ({free_mb:,} MB available)")
        print("   Model download requires ~1-2GB")

    # Login to HuggingFace if token is provided
    if hf_token:
        print("🔐 Authenticating with HuggingFace...")
        try:
            login(token=hf_token)
            print("✅ Authentication successful")
        except Exception as e:
            print(f"⚠️  Authentication failed: {e}")
            print("   Continuing without authentication...")
    else:
        print("⚠️  No HF_TOKEN provided, downloading without authentication")

    # Download the model
    try:
        print(f"📥 Downloading {model_name}...")
        SentenceTransformer(model_name, cache_folder=cache_dir)

    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("   This might be due to network issues or insufficient disk space")
        raise

    print("🎉 Model download completed successfully!")

if __name__ == "__main__":
    main()
