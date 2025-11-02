FROM python:3.11-slim

WORKDIR /app

# Install MySQL client dependencies + dos2unix (CRLF 문제 방지)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend /app
COPY data-pipeline /app/data-pipeline

# Fix Windows line endings + ensure execute permission
RUN dos2unix docker/entrypoint.sh && chmod +x docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
