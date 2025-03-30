#!/bin/bash

PORT=${PORT:-8000}
echo "Starting FastAPI server on port $PORT"
uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
