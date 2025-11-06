#!/bin/bash
set -e
python download_models.py
exec uvicorn src.backend.main:app --host 0.0.0.0 --port 8080
