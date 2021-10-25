import PySimpleGUI as sg
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

sg.theme('LightBlue2')
layout = [[sg.Text('Input_file  '), sg.InputText(key='_input_file_'), sg.FileBrowse(), sg.Button(button_text='FFT')]]
window = sg.Window('FFT', layout)

while True:
    event, values = window.read()
    if event in (None, 'Exit', 'Cancel'):
        break

    if event == 'FFT':
        img = Image.open('{}'.format(values['_input_file_'])).convert("1")
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = np.log10(np.abs(fshift) + 10)

        plt.subplot(121), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('Spectrum'), plt.xticks([]), plt.yticks([])
        plt.show()


