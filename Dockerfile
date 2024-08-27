# Using a Python base image
FROM python:3.10-slim

# Install the necessary packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    poppler-utils \
    libopencv-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries via pip
RUN pip install --no-cache-dir \
    pytesseract \
    pdf2image \
    pillow \
    opencv-python-headless \
    loguru

# Set the working directory
WORKDIR /app

# Copy the Python script
COPY main_file_for_docker.py /app/main.py

# Specify the command to launch the application
CMD ["python", "main_file_for_docker.py"]
