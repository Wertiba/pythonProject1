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

#photo connection
img = cv2.imread('photos/photo_2024-08-20_15-49-35.jpg')

#loguru setting
#logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')


@logger.catch()
def refactor(img):
    again = False
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #getting text from image
    text = (pytesseract.image_to_string(img, config=config, lang='rus'))
    logger.info(text)

    # coordinates of words
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # finding the secret word
    tags = re.finditer(
        r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s*)([а-яА-Яa-zA-Z\-_]+)(\.?)(\n?)', text)
    secret_words = [tag for tag in tags]
    logger.info(secret_words)


    for i, el in enumerate(data.splitlines()):
        #first iteration skip
        if i == 0:
            continue

        el = el.split()
        x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])

        try:
            #remove other symbols
            symbols_to_remove = ",!?."
            for symbol in symbols_to_remove:
                el[11] = el[11].replace(symbol, "")

            logger.info(el[11])


            if again == True:
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
                again = False

            for word in secret_words:
                if str(el[11]).lower() == str(word.group(31)).lower():
                    cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)

                    if str(el[11]).lower()[-1] == '-' or '—':
                        again = True

                    if str(word.group(33)) == '\n':
                        again = True


        except IndexError:
            logger.warning('Операция пропущена')

    return img


def extract_and_process_images_in_memory(pdf_path, processed_pdf_path='processed_output.pdf'):
    # Конвертируем страницы PDF в изображения (объекты Pillow)
    pages = convert_from_path(pdf_path, poppler_path=r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin")

    processed_images = []
    for page in pages:
        # Конвертируем страницу из Pillow в формат, пригодный для OpenCV (numpy array)
        page_np = np.array(page)
        page_cv = cv2.cvtColor(page_np, cv2.COLOR_RGB2BGR)

        # Пример обработки: конвертация в черно-белое изображение
        gray_image = refactor(page_cv)

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


if __name__ == '__main__':
    # cv2.imshow('result', refactor(img))
    # cv2.waitKey(0)
    extract_and_process_images_in_memory('pdf/doc20240820153531130462.pdf')
