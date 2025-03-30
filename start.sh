#!/bin/bash

# Use Railway-provided $PORT or default to 8000 for local dev
PORT=${PORT:-8000}

echo "🚀 Launching FastAPI app on port $PORT..."
echo "📁 Working directory: $(pwd)"
echo "🧪 Contents:"
ls -la

echo "🧠 Python version: $(python --version)"
echo "🛠️ Starting Uvicorn..."

# Start the FastAPI app
exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
