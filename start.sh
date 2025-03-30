#!/bin/bash

# Default to 8000 if $PORT is not set
PORT=${PORT:-8000}

echo "Launching FastAPI on port $PORT"
uvicorn api.main:app --host 0.0.0.0 --port "$PORT" 