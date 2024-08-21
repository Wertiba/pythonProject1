from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
import io


def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='processed_output.pdf'):
    # Конвертируем страницы PDF в изображения (объекты Pillow)
    pages = convert_from_path(pdf_path, poppler_path=r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin")

    processed_images = []
    for page in pages:
        # Конвертируем страницу из Pillow в формат, пригодный для OpenCV (numpy array)
        page_np = np.array(page)
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)

        # Пример обработки: конвертация в черно-белое изображение
        gray_image = cv2.cvtColor(page_cv, cv2.COLOR_BGR2GRAY)

        # Конвертируем обратно в формат, пригодный для Pillow
        processed_image_pil = Image.fromarray(gray_image).convert('RGB')

        # Добавляем обработанное изображение в список
        processed_images.append(processed_image_pil)

    # Конвертируем все обработанные изображения в один PDF
    if processed_images:
        processed_images[0].save(
            processed_pdf_path, save_all=True, append_images=processed_images[1:]
        )
        print(f"Обработанные изображения объединены в PDF: {processed_pdf_path}")


# Использование функции
extract_and_process_images_in_memory('pdf/sample_pdf.pdf')
