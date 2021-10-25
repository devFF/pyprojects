from PIL import Image
import os
import xlsxwriter

workbook = xlsxwriter.Workbook('Out' + '.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, 'Filename')  # Строка, столбец, значение
worksheet.write(0, 1, 'Black')
worksheet.write(0, 2, 'White')
worksheet.write(0, 3, 'Gray')

filename_list, black_list, white_list, gray_list = list(), list(), list(), list()

def count_pixel(im):
    image = Image.open(im).convert("RGB")
    black = 0
    white = 0
    gray = 0
    for pixel in image.getdata():
        if pixel[0] < 100 and pixel[1] < 100 and pixel[2] < 100:
            black += 1
        elif pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
            white += 1
        else:
            gray += 1
    if im not in filename_list:
        filename_list.append(im)
        black_list.append(black)
        white_list.append(white)
        gray_list.append(gray)

    out_str_full = '{} black = {} white = {} gray = {} \n'.format(im,black,white,gray)
    black = str(black)+' \n'
    white = str(white) + ' \n'
    gray = str(gray) + ' \n'
    return out_str_full, black, white, gray

with open('Out_full.txt', 'w') as f:
    f.close()
with open('Out_black.txt', 'w') as f:
    f.close()
with open('Out_white.txt', 'w') as f:
    f.close()
with open('Out_gray.txt', 'w') as f:
    f.close()

Pict_format = ('.jpg', '.jpeg', '.png', '.bmp')

for file in os.listdir():
    if file.endswith(Pict_format):
        with open('Out_full.txt', 'a') as f:
            f.write(count_pixel(im=file)[0])
        with open('Out_black.txt', 'a') as f:
            f.write(count_pixel(im=file)[1])
        with open('Out_white.txt', 'a') as f:
            f.write(count_pixel(im=file)[2])
        with open('Out_gray.txt', 'a') as f:
            f.write(count_pixel(im=file)[3])

for i in range(len(filename_list)):
    print(i, len(filename_list))
    worksheet.write(i+1, 0, filename_list[i])
    worksheet.write(i+1, 1, black_list[i])
    worksheet.write(i+1, 2, white_list[i])
    worksheet.write(i+1, 3, gray_list[i])
workbook.close()