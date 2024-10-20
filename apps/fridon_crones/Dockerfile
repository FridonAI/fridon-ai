FROM python:3.11-buster as builder

RUN pip install poetry==1.8.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY ../../libs/core libs/core
COPY ../../pyproject.toml ../../poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.11-slim-buster as runtime

WORKDIR /app


ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY apps/fridon_crones /app/apps/fridon_crones
COPY ./settings.py /app/settings.py
COPY libs /app/libs
