import fitz
import io

from PIL import Image
from pdfminer.high_level import extract_pages, extract_text

# for page_layout in extract_pages('pdf/PML30_AddmissionWork_2020_Form_08-problems-v2.pdf'):
#     for element in page_layout:
#         print(element)
# text = extract_text('pdf/PML30_AddmissionWork_2020_Form_08-problems-v2.pdf')
# print(text)

i1 = Image.open('photos/photo_2024-08-15_11-07-28.jpg')
i2 = Image.open('photos/photo_2024-08-14_12-52-19.jpg')
i3 = Image.open('photos/photo_2024-08-13_15-28-38.jpg')

il = [i2, i3]

i1.save('C:\\Users\\wertiba\\PycharmProjects\\pythonProject1\\pdf\\test3.pdf', 'PDF', resolution=100, save_all=True, append_images=il)
