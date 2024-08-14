import cv2
import pytesseract
import re

#путь для подключения tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#подключение фото
img = cv2.imread('photos/photo_2024-08-14_12-04-06.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#будет выведен весь текст с картинки
config = r'--oem 3 --psm 6'
text = (pytesseract.image_to_string(img, config=config, lang='rus+eng'))

#координаты слов
data = pytesseract.image_to_data(img, config=config, lang='rus')
def find_word():
    tags = re.finditer(r"кодовое слово (\S+)", text)
    # for tag in tags:
    #     word = tag.group(1)
    #
    #     return word
    list = [tag.group(1) for tag in tags]
    return list


for i, el in enumerate(data.splitlines()):
    if i == 0:
        continue

    el = el.split()

    try:
        x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])

        for word in find_word():
            if el[11] == word:
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)

    except IndexError:
        # print('Операция пропущена')
        pass



cv2.imshow('result', img)
cv2.waitKey(0)
