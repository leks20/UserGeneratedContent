FROM python:3.10

WORKDIR /app

RUN pip install clickhouse_driver pydantic

COPY client.py .

CMD ["tail", "-f", "/dev/null"]
