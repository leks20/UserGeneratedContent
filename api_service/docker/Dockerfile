FROM python:3.10

ENV C_FORCE_ROOT=True
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/code

WORKDIR /code
RUN python -m pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir poetry


COPY pyproject.toml poetry.lock /code/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .
