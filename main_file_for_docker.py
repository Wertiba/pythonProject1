import cv2
import pytesseract
import re
import sys
import numpy as np

from pdf2image import convert_from_path
from PIL import Image
from loguru import logger

# Tesseract configuration for OCR (Optical Character Recognition)
config = r'--oem 3 --psm 6'

# Loguru settings for logging with a rotating log file of 1 MB and compression
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 MB', compression='zip')

# Initialize the page counter for processing multiple PDF pages
page_counter = 1

# Function to extract specific secret words from the OCR'd text using a regex pattern
def extract_secret_words(text):
    # Regex pattern to match the specific secret words
    pattern = r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s*)([а-яА-Яa-zA-Z\-_]+)(\.?)(\n?)'
    return list(re.finditer(pattern, text))

# Function to clean words by removing specified symbols and converting to lowercase
def clean_word(word, symbols_to_remove=",!?."):
    return word.translate(str.maketrans('', '', symbols_to_remove)).strip().lower()

# Function to process the image and redact specific words
def refactor(img):
    counter = 0
    # Convert the image to RGB for Tesseract OCR
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Perform OCR to extract text from the image
    text = pytesseract.image_to_string(img, config=config, lang='rus')
    logger.debug(f'text received: {text}')

    # Get detailed OCR data including word positions
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # Extract secret words based on the regex pattern
    secret_words = extract_secret_words(text)
    logger.debug(f'secret words received: {secret_words}')

    draw_black_rect = False

    # Loop through each line of OCR data to find and redact secret words
    for i, line in enumerate(data.splitlines()):
        if i == 0:
            continue  # Skip the header line

        elements = line.split()
        if len(elements) < 12:
            logger.warning('Operation skipped due to insufficient elements')
            continue  # Skip if the line doesn't have enough elements

        # Extract position and size of the current word
        x, y, w, h = map(int, elements[6:10])
        # Clean and normalize the current word
        current_word = clean_word(elements[11].lower())

        # If the previous word was hyphenated, draw a black rectangle over it
        if draw_black_rect:
            cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
            logger.info(f'the rectangle is drawn (hyphenation), coordinates: {x, y, w, h}')
            draw_black_rect = False

        # Check if the current word matches any secret words
        for word in secret_words:
            if current_word == word.group(31).lower():
                counter += 1
                # Draw a black rectangle over the secret word
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
                logger.info(f'the rectangle is drawn, coordinates: {x, y, w, h}')

                # Check for hyphenation or line breaks to continue redaction
                if current_word.endswith(('-', '—')) or word.group(33) == '\n':
                    draw_black_rect = True

    # Log a message if the number of secret words matches the redacted words
    if len(secret_words) <= counter:
        logger.info('the number of secret words is more or matches the number of rectangles drawn without hyphens, everything is OK')
    else:
        logger.error(f'the number of secret words is less than the number of drawn rectangles without hyphens, it is recommended to check the page manually (page: {page_counter})')

    return img

# Function to extract images from a PDF, process them, and save the output as a new PDF
def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='/app/output/processed_output.pdf'):
    global page_counter
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path)
    processed_images = []

    for page in pages:
        logger.info(f'page {page_counter}')
        # Convert PIL image to a NumPy array for OpenCV processing
        page_np = np.array(page)
        # Convert RGB to BGR for OpenCV
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)
        logger.info('the image has been converted to the required format')

        # Process the image to redact secret words
        image_with_rect = refactor(page_cv)
        # Convert the processed image back to PIL format
        processed_image_pil = Image.fromarray(image_with_rect).convert('RGB')
        logger.info('image processed')

        # Add the processed image to the list
        processed_images.append(processed_image_pil)
        page_counter += 1

    # Save all processed images as a single PDF
    if processed_images:
        logger.info(f"Saving processed PDF to {processed_pdf_path}")
        processed_images[0].save(
            processed_pdf_path, save_all=True, append_images=processed_images[1:]
        )
        logger.info(f"Processed PDF saved to {processed_pdf_path}")

# Main function to handle command-line arguments and start processing
@logger.catch()
def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python main.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extract_and_process_images_in_memory(pdf_path)

# Entry point of the script
if __name__ == '__main__':
    main()
