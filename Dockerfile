# Base image for running kaizen
FROM python:3.13-slim

# Install git and poetry in a single RUN command to reduce layers
RUN apt update && apt install -y git \
    && pip3 install poetry \
    && rm -rf /var/lib/apt/lists/*

# Set up application directory
WORKDIR /app

# Copy all files to the app directory
COPY . /app

# Build and install the application, then clean up
RUN poetry build && pip install --no-cache-dir dist/*.whl \
    && rm -rf dist

# Set the default command to run the application
CMD ["kaizen"]
