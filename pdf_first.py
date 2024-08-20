import fitz
import io

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from PIL import Image
from pdfminer.high_level import extract_pages, extract_text

# for page_layout in extract_pages('pdf/PML30_AddmissionWork_2020_Form_08-problems-v2.pdf'):
#     for element in page_layout:
#         print(element)
# text = extract_text('pdf/PML30_AddmissionWork_2020_Form_08-problems-v2.pdf')
# print(text)

pdf = fitz.open('pdf/7-kl__биология.pdf')
counter = 1

for i in range(10):
    page = pdf[i]
    images = page.get_images()

    try:
        for image in images:
            base_img = pdf.extract_image(image[0])
            image_data = base_img['image']
            img = Image.open(io.BytesIO(image_data))
            extension = base_img['ext']
            img.save(open(f'photos/for_pdf/image{counter}.{extension}', 'wb'))
            counter += 1
    except OSError:
        pass





i1 = Image.open('photos/for_pdf/image1.jpeg')

il = [f'photos/for_pdf/image{i}.jpeg' for i in range(10)]
# i2 = Image.open('photos/photo_2024-08-14_12-52-19.jpg')
# i3 = Image.open('photos/photo_2024-08-13_15-28-38.jpg')
#
# il = [i2, i3]

i1.save('C:\\Users\\wertiba\\PycharmProjects\\pythonProject1\\pdf\\test4.pdf', 'PDF', resolution=100, save_all=True, append_images=il)
