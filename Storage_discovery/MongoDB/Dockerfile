FROM python:3.10

WORKDIR /app

ADD . /app

RUN pip install motor faker

COPY mongo_discovery.py .

CMD ["tail", "-f", "/dev/null"]
