from pdf2image import convert_from_path
from loguru import logger

@logger.catch()
def main():
    poppler_path = r"C:\Users\wertiba\Documents\Install\Release-24.07.0-0\poppler-24.07.0\Library\bin"

    pdf_path = str(input('Скопируйте сюда полный путь до pdf документа: '))
    pdf_path = clean_word(pdf_path, symbols_to_remove='\"')



    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    logger.info(pdf_path)

def clean_word(word, symbols_to_remove=",!?."):
    return word.translate(str.maketrans('', '', symbols_to_remove)).strip().lower()


if __name__ == '__main__':
    main()
