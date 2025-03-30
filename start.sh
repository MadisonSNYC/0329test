#!/bin/bash
set -e

# Use Railway's provided PORT or fallback to 8000
PORT=${PORT:-8000}

echo "Starting server on port $PORT"
exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
