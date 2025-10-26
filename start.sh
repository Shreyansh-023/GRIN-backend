#!/bin/bash
set -e

PORT="${PORT:-8000}"
export PYTHONPATH="${PYTHONPATH:-.}"
export PYTORCH_NO_CUDA_MEMORY_CACHING=1
export PYTORCH_NO_CUDA=1

exec waitress-serve --host=0.0.0.0 --port="${PORT}" app:app