#!/usr/bin/env python3
"""
Optimized script for model downloading in multi-stage Docker builds.
Checks if models already exist in cache before attempting download.
Includes space monitoring and cleanup functionality.
"""

import os
import shutil
from pathlib import Path
from huggingface_hub import login
from sentence_transformers import SentenceTransformer

def get_disk_space(path: str = "/") -> tuple[int, int]:
    """Get available and total disk space in MB."""
    stat = shutil.disk_usage(path)
    return stat.free // (1024 * 1024), stat.total // (1024 * 1024)

def find_model_in_cache(cache_dir: Path, model_name: str, max_depth: int = 4) -> Path | None:
    """
    Recursively search for model directory in HF_HOME cache.

    Searches subdirectories up to max_depth levels and matches folder names
    containing the model identifier. This approach is independent of the
    internal cache structure that SentenceTransformer uses.
    """
    model_identifier = model_name.split('/')[-1]  # Get last part: "multilingual-e5-base"

    def search_recursive(current_dir: Path, current_depth: int) -> Path | None:
        if current_depth > max_depth:
            return None

        try:
            for item in current_dir.iterdir():
                if item.is_dir():
                    # Check if directory name matches our model identifier
                    if model_identifier in item.name:
                        # Verify it's not empty and contains model files
                        if any(item.iterdir()):
                            return item

                    # Recursively search subdirectories
                    result = search_recursive(item, current_depth + 1)
                    
                    if result:
                        return result
        except OSError:
            # Skip directories we can't read
            pass

        return None

    return search_recursive(cache_dir, 0)

def check_model_exists(cache_dir: str, model_name: str) -> bool:
    """
    Check if model already exists in HF_HOME cache using recursive search.

    This approach is independent of SentenceTransformer's internal cache structure
    and works by finding directories that contain the model identifier.
    """
    # Check if HF_HOME directory exists
    hf_cache_path = Path(cache_dir)

    if not hf_cache_path.exists():
        print(f"📁 Cache directory {cache_dir} does not exist")
        return False

    print(f"🔍 Searching for model {model_name} in cache...")
    print(f"📁 Cache directory contents: {list(hf_cache_path.iterdir())}")

    # Find model directory recursively
    model_dir = find_model_in_cache(hf_cache_path, model_name)

    if not model_dir:
        print(f"🔍 No cache directory found for model {model_name}")
        return False

    print(f"📁 Found model cache at: {model_dir}")
    print(f"📁 Model directory contents: {list(model_dir.iterdir())}")

    # Final verification: Check for required model files instead of loading
    print("🔍 Verifying model files exist in cache...")

    # Look for model files more comprehensively
    config_files = list(model_dir.glob("**/config.json"))
    bin_files = list(model_dir.glob("**/*.bin"))
    safetensors_files = list(model_dir.glob("**/*.safetensors"))

    print(f"📄 Found config files: {config_files}")
    print(f"📄 Found .bin files: {bin_files}")
    print(f"📄 Found .safetensors files: {safetensors_files}")

    # Check if we have the required files
    has_config = len(config_files) > 0
    has_model_files = len(bin_files) > 0 or len(safetensors_files) > 0

    if has_config and has_model_files:
        print("✅ Required model files found in cache")
        return True
    else:
        print(f"⚠️  Required model files missing in {model_dir}")
        print(f"   Config files found: {has_config}")
        print(f"   Model files found: {has_model_files}")
        print("   Will re-download the model")
        return False

def main():
    # Environment variables
    hf_token = os.getenv("HF_TOKEN")
    cache_dir = os.getenv("HF_HOME", "/app/.cache/huggingface")
    model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

    print("🤖 Mar.IA Model Downloader")
    print(f"📁 Cache directory: {cache_dir}")
    print(f"🎯 Target model: {model_name}")

    # Check disk space
    free_mb, total_mb = get_disk_space()
    print(f"💾 Available disk space: {free_mb:,} MB / {total_mb:,} MB")

    if free_mb < 2048:  # Less than 2GB free
        print(f"⚠️  WARNING: Low disk space ({free_mb:,} MB available)")
        print("   Model download requires ~1-2GB")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Check if model already exists
    if check_model_exists(cache_dir, model_name):
        print(f"✅ Model already cached in {cache_dir}")
        print("🚀 Skipping download - using cached model")
        return

    print("📥 Model not found in cache, starting download...")

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
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    main()
