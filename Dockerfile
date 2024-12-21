# Base image for running kaizen
FROM python:3.13-slim

RUN apt update && apt install -y git

RUN pip3 install poetry

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN poetry install --no-dev
