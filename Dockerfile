FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
