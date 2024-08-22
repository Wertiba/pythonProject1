import cv2
import pytesseract
import re
import numpy as np

from pdf2image import convert_from_path
from PIL import Image
from loguru import logger

#connection tesseract and poppler
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'

poppler_path=r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin"

#loguru setting
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 MB', compression='zip')


def extract_secret_words(text):
    pattern = r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s*)([а-яА-Яa-zA-Z\-_]+)(\.?)(\n?)'
    return list(re.finditer(pattern, text))


def clean_word(word, symbols_to_remove=",!?."):
    for symbol in symbols_to_remove:
        word = word.replace(symbol, "")
    return word


def refactor(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Получение текста с изображения
    text = pytesseract.image_to_string(img, config=config, lang='rus')
    logger.info(text)

    # Координаты слов
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # Поиск "секретных" слов
    secret_words = extract_secret_words(text)
    logger.info(secret_words)

    draw_black_rect = False

    for i, line in enumerate(data.splitlines()):
        if i == 0:
            continue

        elements = line.split()
        if len(elements) < 12:
            logger.warning(f'Операция пропущена из-за количества элементов')
            continue

        x, y, w, h = map(int, elements[6:10])
        current_word = clean_word(elements[11].lower())

        if draw_black_rect:
            cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
            draw_black_rect = False

        for word in secret_words:
            if current_word == word.group(31).lower():
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)

                # Проверяем наличие дефиса и условия для продолжения
                if current_word.endswith(('-', '—')) or word.group(33) == '\n':
                    draw_black_rect = True
    return img


def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='processed_output.pdf'):
    # Конвертируем страницы PDF в изображения (объекты Pillow)
    pages = convert_from_path(pdf_path, poppler_path=r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin")
    processed_images = []

    for page in pages:
        # Конвертируем страницу из Pillow в формат, пригодный для OpenCV (numpy array)
        page_np = np.array(page)
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)

        # Обработка изображения
        image_with_rect = refactor(page_cv)

        # Конвертируем обратно в формат, пригодный для Pillow
        processed_image_pil = Image.fromarray(image_with_rect).convert('RGB')

        # Добавляем обработанное изображение в список
        processed_images.append(processed_image_pil)

    # Конвертируем все обработанные изображения в один PDF
    if processed_images:
        processed_images[0].save(
            processed_pdf_path, save_all=True, append_images=processed_images[1:]
        )
        logger.info(f"Обработанные изображения объединены в PDF: {processed_pdf_path}")

@logger.catch()
def main():
    pdf_path = str(input('Скопируйте сюда полный путь до pdf документа: '))
    extract_and_process_images_in_memory(pdf_path)


if __name__ == '__main__':
    main()
