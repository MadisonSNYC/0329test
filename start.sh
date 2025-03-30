#!/bin/bash

# Use Railway-provided $PORT or default to 8000 for local dev
PORT=${PORT:-8000}

# Launch the FastAPI app
exec uvicorn api.index:app --host 0.0.0.0 --port "$PORT"
