FROM python:3.11.6-slim

WORKDIR /app

COPY alembic.ini .
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY setup.py .
COPY setup.cfg .

RUN pip install -e .

COPY .env .

COPY core ./core
COPY bot_ui ./bot_ui
