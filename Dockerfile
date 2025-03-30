FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . .

# Set the default port
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 