FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}" 