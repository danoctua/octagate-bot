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

COPY indexer ./indexer
COPY core ./core

# Stage 2: Build the indexer image
FROM octagate-base AS indexer

COPY indexer/requirements.txt requirements-indexer.txt
RUN pip install -r requirements-indexer.txt


# Stage 3: Build the community-manager image
FROM octagate-base AS community-manager

COPY community_manager/requirements.txt requirements-community-manager.txt
RUN pip install -r requirements-community-manager.txt

COPY community_manager ./community_manager

# Stage 4: FastAPI application
FROM octagate-base AS api

COPY api/requirements.txt requirements-api.txt
RUN pip install -r requirements-api.txt

COPY api ./api

# Stage 5: Scheduler image
FROM community-manager AS scheduler

COPY scheduler ./scheduler
