FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ensure the startup script is executable at runtime
RUN chmod +x start.sh

# This is the key change that fixes the permission issue:
ENTRYPOINT ["sh", "./start.sh"]
