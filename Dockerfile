# Базовый образ с Python
FROM python:3.9-slim

# Устанавливаем зависимости для работы с изображениями и PDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    libgl1-mesa-glx \
    libglib2.0-0 \
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
    loguru \
    flask \
    waitress

# Создаем необходимые директории для входных и выходных файлов
RUN mkdir -p /app/input /app/output

# Копируем код приложения в контейнер
COPY main_file_for_docker.py /app/

# Устанавливаем рабочую директорию
WORKDIR /app

EXPOSE 8000

# Запускаем приложение
CMD ["waitress-serve", "--port=8000", "main_file_for_docker:app"]
