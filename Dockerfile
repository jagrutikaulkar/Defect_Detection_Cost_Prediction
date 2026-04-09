FROM python:3.11-slim

# Install system dependencies for TensorFlow and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libblas-dev \
    liblapack-dev \
    gfortran \
    libglib2.0-0 \
    libglib2.0-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render uses dynamic PORT env var)
EXPOSE 10000

# Set environment variables
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PORT=10000

# Run the app with gunicorn (respects PORT env var)
CMD exec gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 300 --workers 2 app:app
