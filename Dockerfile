FROM python:3.11-slim

# Install system dependencies for OpenCV, TensorFlow, and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libblas-dev \
    liblapack-dev \
    gfortran \
    libxcb1 \
    libx11-6 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libglib2.0-dev \
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libglvnd0 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV TF_ENABLE_ONEDNN_OPTS=0

# Run the app
CMD ["python", "app.py"]
