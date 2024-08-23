import cv2
import pytesseract
import re
import numpy as np

from pdf2image import convert_from_path
from PIL import Image
from loguru import logger

# Connecting Tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'

# Path to Poppler binaries for PDF conversion
poppler_path = r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin"

# Loguru settings for logging
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 MB', compression='zip')

page_counter = 1


def extract_secret_words(text):
    # Regex pattern to match the "secret word" phrase with variations, including hyphenation and line breaks
    pattern = r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s*)([а-яА-Яa-zA-Z\-_]+)(\.?)(\n?)'
    return list(re.finditer(pattern, text))


def clean_word(word, symbols_to_remove=",!?."):
    # Remove specified symbols and convert word to lowercase
    return word.translate(str.maketrans('', '', symbols_to_remove)).strip().lower()


def refactor(img):
    counter = 0
    # Convert image from BGR to RGB format
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Extract text from the image using Tesseract
    text = pytesseract.image_to_string(img, config=config, lang='rus')
    logger.debug(f'text received: {text}')

    # Get word coordinates and other details from the image
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # Find "secret words" in the extracted text
    secret_words = extract_secret_words(text)
    logger.debug(f'secret words received: {secret_words}')

    # Flag to handle word continuation after hyphens or line breaks
    draw_black_rect = False

    for i, line in enumerate(data.splitlines()):
        if i == 0:
            # Skip first iteration
            continue

        elements = line.split()
        if len(elements) < 12:
            # Skip lines that do not have enough elements
            logger.warning('Operation skipped due to insufficient elements')
            continue

        # Extract coordinates and dimensions for drawing rectangles
        x, y, w, h = map(int, elements[6:10])
        current_word = clean_word(elements[11].lower())

        if draw_black_rect:
            # Draw a black rectangle over the previous word if needed
            cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
            logger.info(f'the rectangle is drawn (hyphenation), coordinates: {x, y, w, h}')
            draw_black_rect = False

        for word in secret_words:
            # Check if the current word matches a "secret word"
            if current_word == word.group(31).lower():
                counter += 1
                # Draw a black rectangle over the matched word
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
                logger.info(f'the rectangle is drawn, coordinates: {x, y, w, h}')

                # Check for hyphenation or line breaks to continue
                if current_word.endswith(('-', '—')) or word.group(33) == '\n':
                    draw_black_rect = True

    if len(secret_words) <= counter:
        logger.info('the number of secret words is more or matches the number of rectangles drawn without hyphens, everything is OK')
    else:
        logger.error(f'the number of secret words is less than the number of drawn rectangles without hyphens, it is recommended to check the page manually (page: {page_counter})')

    return img


def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='processed_output.pdf'):
    global page_counter
    # Convert PDF pages to images (Pillow objects)
    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    processed_images = []

    for page in pages:
        logger.info(f'page {page_counter}')
        # Convert the page from Pillow to OpenCV format (numpy array)
        page_np = np.array(page)
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)
        logger.info('the image has been converted to the required format')

        # Process the image (apply blackout based on secret words)
        image_with_rect = refactor(page_cv)

        # Convert back to Pillow format for PDF output
        processed_image_pil = Image.fromarray(image_with_rect).convert('RGB')
        logger.info('image processed')

        # Add the processed image to the list
        processed_images.append(processed_image_pil)

        page_counter += 1

    # Combine all processed images into a single PDF
    if processed_images:
        processed_images[0].save(
            processed_pdf_path, save_all=True, append_images=processed_images[1:]
        )
        logger.info(f"Processed images merged into PDF: {processed_pdf_path}")


@logger.catch()
def main():
    pdf_path = clean_word(str(input('Copy the full path to the PDF document: ')), symbols_to_remove='\"')
    extract_and_process_images_in_memory(pdf_path)


if __name__ == '__main__':
    main()
