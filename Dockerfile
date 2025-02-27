# Use multi-stage build for optimal image size

# Backend build stage
FROM python:3.9-slim as backend-build

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend build stage
FROM node:16-alpine as frontend-build

WORKDIR /app

# Copy frontend files - modified to only look for package.json
COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from backend-build
COPY --from=backend-build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend-build /usr/local/bin /usr/local/bin

# Copy React build files
COPY --from=frontend-build /app/build /app/frontend/build

# Copy backend code
COPY backend/ /app/backend/

# Create data directory
RUN mkdir -p /app/data/images && \
    chmod -R 777 /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py
ENV DATA_DIR=/app/data

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:create_app()"]