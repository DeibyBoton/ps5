FROM python:3.11-alpine

WORKDIR /app

COPY . /app

EXPOSE 8080 53/udp

CMD ["python3", "server.py"]
