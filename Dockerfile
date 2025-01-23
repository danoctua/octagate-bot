# Stage 1: Build the base image with the core package
FROM python:3.11.6-slim AS octagate-base

# Set environment variables
ENV PYTHONUNBUFFERED=1

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

# Stage 3: Build the wallet-indexer image
FROM octagate-base AS wallet-indexer

COPY wallet_indexer/requirements.txt requirements-wallet-indexer.txt
RUN pip install -r requirements-wallet-indexer.txt


# Stage 4: Build the community-manager image
FROM octagate-base AS community-manager

COPY community_manager/requirements.txt requirements-community-manager.txt
RUN pip install -r requirements-community-manager.txt

COPY community_manager ./community_manager
