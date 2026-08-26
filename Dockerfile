FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts ./scripts
COPY dashboard ./dashboard
COPY config ./config
COPY scheduler ./scheduler
COPY tests ./tests

RUN mkdir -p /app/data/raw

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8501