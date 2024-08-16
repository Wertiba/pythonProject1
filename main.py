import cv2
import pytesseract
import re

#tesseract connection
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'

#photo connection
img = cv2.imread('photos/photo_2024-08-15_11-07-28.jpg')


def refactor(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #getting text from image
    text = (pytesseract.image_to_string(img, config=config, lang='rus+eng'))
    print(text)

    # coordinates of words
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # finding the secret word
    tags = re.finditer(
        r'(ко)(.?)(-|—?)(.?)(\s*)(.?)(до)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(-|—?)(\s*)(.?)(е)(.?)(\s)(.?)(сло)(.?)(-|—?)(.?)(\s*)(.?)(во)(.?)(\s+)([а-яА-Яa-zA-Z\-_'
        r']+)', text)
    secret_words = [tag.group(31) for tag in tags]
    print(secret_words)


    for i, el in enumerate(data.splitlines()):
        #first iteration skip
        if i == 0:
            continue

        el = el.split()

        try:
            #remove other symbols
            symbols_to_remove = ",!?."
            for symbol in symbols_to_remove:
                el[11] = el[11].replace(symbol, "")


            print(el[11])
            x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])

            for word in secret_words:
                if el[11] == word:
                    cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)

                # elif str(el[11])[-1] == '-':
                #     print('!!!!!')



        except IndexError:
            # print('Операция пропущена')
            pass

    return img

if __name__ == '__main__':
    cv2.imshow('result', refactor(img))
    cv2.waitKey(0)
