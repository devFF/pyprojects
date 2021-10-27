import requests
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter import scrolledtext
from tkinter import ttk
import os
import geocoder
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from io import BytesIO

class App:
    def __init__(self):
        # Узнаем имя пользователя
        name = os.getlogin()

        # Узнаем местоположение пользователя
        self.city = self.user_location()
        self.city_base = self.city_list()

        # Создаем рабочую область и тему
        self.window = tk.Tk()
        self.window.title("Weather caster")
        self.window.geometry('800x600')
        #self.window.tk.call("source", "sun-valley.tcl")
        #self.window.tk.call("set_theme", "light")

        # Уточняем местоположение пользователя
        self.city_mes = tk.messagebox.askquestion(title='Location',
                                                  message='Hello, {}, are you from {}?'.format(name, self.city))
        # Выбор города ТЕКСТ СЛЕВА ОТ БОКСА ВЫБОРА ГОРОДА
        self.greetings = tk.Label(self.window,
                                  text='Select city:',
                                  font=('Times New Roman', 20),
                                  justify='left', width=9)
        self.greetings.grid(column=0, row=0, sticky='w')

        # Получаем список городов России и добавляем текущий город в общий список
        self.city_list = self.city_list()
        self.city_list.append(self.city)

        # Создаем БОКС ВЫБОРА ГОРОДА
        self.city_box = Combobox(self.window, font=('Times New Roman', 20), justify='left')
        self.city_box['values'] = self.city_list

        # Обработка диалогового окна Location
        if self.city_mes == 'yes':
            self.city_box.current(len(self.city_list) - 1)
            self.weather_info()
            #self.put_weather_ico = tk.Canvas(self.window, height=50, width=50)
            #self.c_put_weather_ico = self.put_weather_ico.create_image(0, 0, anchor='nw', image=self.get_ico())
            #self.put_weather_ico.grid(row=1, column=2)
        if self.city_mes == 'no':
            messagebox.showinfo(title='Location',
                                message='Choose a city from the list')
            self.city_box.current(0)
            self.weather_info()

        # Определение параметров БОКСА ВЫБОРА ГОРОДА
        self.city_box.grid(column=0, row=0, sticky='w', padx=125)
        # Вызов функции при выборе другого города
        self.city_box.bind("<<ComboboxSelected>>",
                           lambda event: self.weather_info())

        # Главный цикл программы
        self.window.mainloop()


    def weather_info(self, event = None):
        """Обновляет информацию о погоде"""
        self.city = self.city_box.get()
        self.weather = self.my_weather(city=self.city)
        self.temperature = self.get_temperature(value='temp')
        self.real_temperature = self.get_temperature(value='feels_like')
        self.image = ImageTk.PhotoImage(Image.open(self.get_ico()))  # Создаем иконку погоды
        # Удаляем информацию о предыдущем городе
        if len(self.window.grid_slaves()) > 1:
            for i, value in enumerate(self.window.grid_slaves()):
                if '.!label' in str(value):
                    self.window.grid_slaves()[i].destroy()
                    self.window.grid_slaves()[i].destroy()
                    break
        weather_data = tk.Label(
            self.window,
            text='Now temperature in {} is {} C, feels like {} C'.format(self.city,
                                                                         self.temperature,
                                                                         self.real_temperature),
            font=('Times New Roman', 18), justify='left')
        weather_data.grid(column=0, row=1, sticky='w')

        #Добавляем иконку текущей погоды напротив строчки
        weather_image = tk.Label(self.window, image=self.image)
        weather_image.grid(column=1, row=1, sticky='w')



    def city_list(self):
        """Парсинг html-таблицы с использованием библиотеки BeautifulSoup. Таблица состоит из 5 столбцов:
        1)Город 2)Регион 3)Федеральный округ 4)lat 5)lng
        Нумерация с 0 до 4, нужен только город => каждый 5 элемент"""
        city_base = []
        try:
            with open('city_base.txt', 'r') as r:
                lines = r.readlines()
                for line in lines:
                    city_base.append(line.replace('\n', ''))
        except:
            url = 'https://on55.ru/articles/2'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find_all('td')
            for i in range(5, len(items)):
                if i % 5 == 0:
                    city_base.append(items[i].get_text())
            with open('city_base.txt', 'w') as w:
                for city in city_base:
                    w.writelines("%s\n" % city)
        return city_base


    def read_api(self):
        """return str with API from file API.txt"""
        try:
            with open('API.txt', 'r') as r:
                api = r.readline().replace('\n', '')
            return api
        except:
            print('Файл API.txt не был найден')


    def user_location(self):
        """Determine user location, return name of the city in STR"""
        loc = geocoder.ipinfo('me').geojson
        loc = loc['features']
        for i, value in enumerate(loc):
            if 'properties' in value:
                loc = loc[i]
                loc = loc['properties']['city']
        return loc


    def my_weather(self, city):
        """Use openweathermap.org to get weathercast in city
        Return content of response"""
        API_KEY = self.read_api()
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city, API_KEY)
        r = requests.get(url)
        content = r.text
        content_json = r.json()
        return (content_json)


    def get_temperature(self, value):
        "Determine temperature from weather"
        ORDER = 2
        try:
            temp_data_in_K = self.weather['main'][value]
            temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
            return temp_data_in_C
        except Exception as ex:
            messagebox.showinfo(title='Error', message='Getting data error')
            print('Входные данные вызвали ошибку ', type(ex))
            return "\nНе удалось узнать {}".format(value)


    def get_ico(self):
        try:
            ico_name = self.weather['weather'][0]['icon']
            ico_url = "https://openweathermap.org/img/wn/%s.png" % ico_name
            response = requests.get(ico_url)
            img = Image.open(BytesIO(response.content))
            img.save('test.png')
            return 'test.png'
        except:
            messagebox.showinfo(title='Error', message='Image download error')


if __name__ == '__main__':
    app = App()

