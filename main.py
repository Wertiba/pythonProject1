import cv2
import pytesseract
import re

#путь для подключения tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#подключение фото
img = cv2.imread('photos/photo_2024-08-14_12-23-56.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#получение текста с картинки
config = r'--oem 3 --psm 6'
text = (pytesseract.image_to_string(img, config=config, lang='rus+eng'))

#координаты слов
data = pytesseract.image_to_data(img, config=config, lang='rus')

#нахождение секретного слова
tags = re.finditer(r"кодовое слово (\S+)", text)
secret_words = [tag.group(1) for tag in tags]


def refactor():
    for i, el in enumerate(data.splitlines()):
        #скип первой итерации
        if i == 0:
            continue

        el = el.split()

        try:
            x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])

            for word in secret_words:
                if el[11] == word:
                    cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)

        except IndexError:
            # print('Операция пропущена')
            pass


if __name__ == '__main__':
    refactor()
    cv2.imshow('result', img)
    cv2.waitKey(0)
