from PIL import Image, ImageDraw
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import os


def delete():
    mydir = os.getcwd()
    filelist = [f for f in os.listdir(mydir) if f.endswith(".bmp") or f.endswith(".png") or f.endswith(".jpeg")]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

def save_and_cut(cut, name, image, pixels, sizeX, sizeY):
    image.save("{}{}x{}_{}pixels.bmp".format(name, sizeX, sizeY, pixels), "bmp")
    if cut:
        imgfile = Path("{}{}x{}_{}pixels.bmp".format(name, sizeX, sizeY, pixels))
        img = Image.open(imgfile)
        img3 = img.crop((0, 0, sizeX - pixels, sizeY - pixels))
        img3.save("{}CUT_{}x{}_{}pixels.bmp".format(name, sizeX, sizeY, pixels))

def draw_pic(cut, pixels, sizeX, sizeY):
    sizeX += sizeX % pixels
    sizeY += sizeY % pixels
    image = Image.new("1", (sizeX, sizeY), color='black')
    draw = ImageDraw.Draw(image)
    k = 0
    if pixels != 1 and sizeX >= 16 and sizeY >= 16:
        for i in range(1, round(sizeY / (2 * pixels)) + 1):
            y = 2 * pixels * i
            for j in range(1, round(sizeX / (2 * pixels)) + 1):
                x = 2 * pixels * j
                if x - 5 < 0:
                    k = 1
                draw.rectangle((x - pixels + k, y - pixels + k, x - 1 + k, y - 1 + k), fill='black')
                draw.rectangle((x - 2 * pixels + k, y - 2 * pixels + k, x - 5 + k, y - 5 + k), fill='white')
        save_and_cut(cut, name='', image=image, pixels=pixels, sizeX=sizeX, sizeY=sizeY)

    if pixels == 1 and sizeX <= 128 and sizeY <= 128:
        for i in range(0, round(sizeY / (2 * pixels)) + 1):
            y = 2 * pixels * i
            for j in range(0, round(sizeX / (2 * pixels)) + 1):
                x = 2 * pixels * j
                draw.point(xy=(x - 1, y - 1), fill='black')
                draw.point(xy=(x, y), fill='white')
        save_and_cut(cut, name="", image=image, pixels=pixels, sizeX=sizeX, sizeY=sizeY)


def draw_line(cut, pixels, sizeX, sizeY):
    sizeX = pixels
    image = Image.new("1", (sizeX, sizeY), color='black')
    draw = ImageDraw.Draw(image)
    for i in range(0, round(sizeY / (2 * pixels))):
        y = 2 * i * pixels
        draw.rectangle((0, y, pixels, y + pixels - 1), fill='white')
        # print(y - pixels, y)
    image.save("LINE_{}x{}_{}pixels.bmp".format(sizeX, sizeY, pixels), "bmp")


def one_dim_vertical(cut, pixels, sizeX, sizeY):
    image = Image.new("1", (sizeX, sizeY), color='black')
    draw = ImageDraw.Draw(image)
    for j in range(0, round(sizeX / (2 * pixels)) + 1):
        x = 2 * pixels * j
        draw.rectangle((x, 0, x + pixels - 1, sizeY), fill='white')
    save_and_cut(cut, name="VERT_", image=image, pixels=pixels, sizeX=sizeX, sizeY=sizeY)


def one_dim_horizontal(cut, pixels, sizeX, sizeY):
    image = Image.new("1", (sizeX, sizeY), color='black')
    draw = ImageDraw.Draw(image)
    for i in range(0, round(sizeX / (2 * pixels)) + 1):
        y = 2 * pixels * i
        draw.rectangle((0, y, sizeX, y + pixels - 1), fill='white')
    save_and_cut(cut, name="HORIZ_", image=image, pixels=pixels, sizeX=sizeX, sizeY=sizeY)

def FFT():
    mydir = os.getcwd()
    filelist = [f for f in os.listdir(mydir) if f.endswith(".bmp")]
    for name in filelist:
        img = Image.open(name).convert("1")
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift+1)) # изменяем(уменьшаем) контраст как логарифмическую функцию

        plt.subplot(121), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('Spectrum'), plt.xticks([]), plt.yticks([])
        #plt.show()
        plt.savefig('{}{}.jpeg'.format('FFT_',name.replace(".bmp","")))
        plt.close()

delete()

for j, size in enumerate([64, 128, 200]):
    draw_line(cut=False, pixels=4, sizeX=4, sizeY=size)
    pass

for i, pixels in enumerate([1, 4]):
    for j, size in enumerate([2, 4, 16, 32, 64, 128, 200]):
        draw_pic(cut=False, pixels=pixels, sizeX=size, sizeY=size)
        pass

for j, size in enumerate([64, 128, 200]):
    one_dim_vertical(cut=False, pixels=4, sizeX=size, sizeY=size)
    one_dim_horizontal(cut=False, pixels=4, sizeX=size, sizeY=size)

FFT()