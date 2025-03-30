#!/bin/sh

# Launch FastAPI on the dynamic Railway port (from env)
exec uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000}
