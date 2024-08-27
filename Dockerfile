# Используем базовый образ Python
FROM python:3.10-slim

# Установим необходимые пакеты
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    poppler-utils \
    libopencv-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установим Python-библиотеки через pip
RUN pip install --no-cache-dir \
    pytesseract \
    pdf2image \
    pillow \
    opencv-python-headless \
    loguru

# Установим рабочую директорию
WORKDIR /app

# Копируем Python-скрипт и другие необходимые файлы
COPY main.py ./

# Указываем команду для запуска приложения
CMD ["python", "main.py"]
