import cv2
import pytesseract
import re
import os
import sys
import numpy as np

from pdf2image import convert_from_path
from PIL import Image
from loguru import logger

# Tesseract configuration
config = r'--oem 3 --psm 6'

# Loguru settings
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 MB', compression='zip')

page_counter = 1


def extract_secret_words(text):
    pattern = r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s*)([а-яА-Яa-zA-Z\-_]+)(\.?)(\n?)'
    return list(re.finditer(pattern, text))


def clean_word(word, symbols_to_remove=",!?."):
    return word.translate(str.maketrans('', '', symbols_to_remove)).strip().lower()


def refactor(img):
    counter = 0
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img, config=config, lang='rus')
    logger.debug(f'text received: {text}')

    data = pytesseract.image_to_data(img, config=config, lang='rus')
    secret_words = extract_secret_words(text)
    logger.debug(f'secret words received: {secret_words}')

    draw_black_rect = False

    for i, line in enumerate(data.splitlines()):
        if i == 0:
            continue

        elements = line.split()
        if len(elements) < 12:
            logger.warning('Operation skipped due to insufficient elements')
            continue

        x, y, w, h = map(int, elements[6:10])
        current_word = clean_word(elements[11].lower())

        if draw_black_rect:
            cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
            logger.info(f'the rectangle is drawn (hyphenation), coordinates: {x, y, w, h}')
            draw_black_rect = False

        for word in secret_words:
            if current_word == word.group(31).lower():
                counter += 1
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
                logger.info(f'the rectangle is drawn, coordinates: {x, y, w, h}')

                if current_word.endswith(('-', '—')) or word.group(33) == '\n':
                    draw_black_rect = True

    if len(secret_words) <= counter:
        logger.info(
            'the number of secret words is more or matches the number of rectangles drawn without hyphens, everything is OK')
    else:
        logger.error(
            f'the number of secret words is less than the number of drawn rectangles without hyphens, it is recommended to check the page manually (page: {page_counter})')

    return img


def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='processed_output.pdf'):
    global page_counter
    pages = convert_from_path(pdf_path)
    processed_images = []

    for page in pages:
        logger.info(f'page {page_counter}')
        page_np = np.array(page)
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)
        logger.info('the image has been converted to the required format')

        image_with_rect = refactor(page_cv)
        processed_image_pil = Image.fromarray(image_with_rect).convert('RGB')
        logger.info('image processed')

        processed_images.append(processed_image_pil)
        page_counter += 1

    if processed_images:
        processed_images[0].save(
            processed_pdf_path, save_all=True, append_images=processed_images[1:]
        )
        logger.info(f"Processed images merged into PDF: {processed_pdf_path}")


@logger.catch()
def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python main.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extract_and_process_images_in_memory(pdf_path)


if __name__ == '__main__':
    main()
