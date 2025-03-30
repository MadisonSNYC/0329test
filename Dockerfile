FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the app
COPY . .

# Use shell to expand $PORT (this is critical)
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT 