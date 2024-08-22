import cv2
import pytesseract
import re
from loguru import logger


#connection tesseract and poppler
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'

poppler_path=r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin"

#photo connection
img = cv2.imread('photos/photo_2024-08-20_15-49-35.jpg')




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

        try:
            elements = line.split()
            if len(elements) < 12:
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

        except IndexError:
            logger.warning('Операция пропущена из-за IndexError')

    return img

cv2.imshow('result', refactor(img))
cv2.waitKey(0)


