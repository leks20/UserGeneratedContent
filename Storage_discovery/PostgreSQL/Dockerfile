FROM python:3.10

WORKDIR /app

ADD . /app

RUN pip install asyncpg faker

COPY pg_discovery.py .

CMD ["tail", "-f", "/dev/null"]
