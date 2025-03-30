FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the app
COPY . .

# Use a small custom entrypoint script instead of relying on $PORT
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"] 