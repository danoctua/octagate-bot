# Stage 1: Build the base image with the core package
FROM python:3.11.6-slim AS octagate-base

# Set environment variables
ENV PYTHONUNBUFFERED=1

RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

WORKDIR /app

COPY alembic.ini .
COPY core/requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY setup.py .
COPY setup.cfg .

RUN pip install -e .

COPY wallet_indexer ./wallet_indexer
COPY core ./core

# Stage 2: Build the telegram-bot image
FROM octagate-base AS telegram-bot

COPY bot_ui/requirements.txt requirements-bot-ui.txt
RUN pip install -r requirements-bot-ui.txt

COPY bot_ui ./bot_ui

# Change ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Stage 3: Build the wallet-indexer image
FROM octagate-base AS wallet-indexer

COPY wallet_indexer/requirements.txt requirements-wallet-indexer.txt
RUN pip install -r requirements-wallet-indexer.txt

# Change ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser
