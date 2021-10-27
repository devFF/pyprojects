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
import datetime
import shutil


class App:
    def __init__(self):
        # Создаем папку Temp для временных файлов
        self.create_temp()

        # Узнаем имя пользователя
        name = os.getlogin()

        # Костыль, задаем количеством строчек Label: используется для их обновления
        self.num_label = 10

        # Узнаем местоположение пользователя
        self.city = self.user_location()

        # Получаем базу городов России
        self.city_base = self.city_list()

        # Узнаем текущую дату в формате год-месяц-число
        self.current_data = self.get_current_data()

        # Создаем рабочую область и тему
        self.window = tk.Tk()
        self.window.title("Weather caster")
        self.window.geometry('720x320')
        # self.window.tk.call("source", "sun-valley.tcl")
        # self.window.tk.call("set_theme", "light")

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
        self.weather = self.my_weather(city=self.city)  # Текущая погода
        self.weather_forecast = self.my_weather_forecast(city=self.city)  # Прогноз погоды
        self.temperature = self.get_temperature(value='temp')  # Текущая температура
        self.real_temperature = self.get_temperature(value='feels_like')  # Текущая реальная температура
        # Удаляем информацию о предыдущем городе чтобы не было наслоения данных друг на друга
        if len(self.window.grid_slaves()) > 1:
            for i, value in enumerate(self.window.grid_slaves()):
                if '.!label' in str(value):
                    for _ in range(self.num_label):
                        self.window.grid_slaves()[i].destroy()
                    break
        weather_data = tk.Label(
            self.window,
            text='Now temperature in {} is {} C, feels like {} C'.format(self.city,
                                                                         self.temperature,
                                                                         self.real_temperature),
            font=('Times New Roman', 18), justify='left')
        weather_data.grid(column=0, row=1, sticky='w')

        # Обрабатываем прогноз погоды, выводим текст прогноза
        self.get_temperature_forecast()

        # Отображаем иконки погоды
        img_list = ['test.png', 'day0.png', 'evening0.png', 'day1.png', 'evening1.png']
        all_lebels = []  # Используется чтобы коллектор мусора пайтона не убирал из памяти иконки погоды
        for i in range(len(img_list)):
            image = ImageTk.PhotoImage(Image.open(img_list[i]))
            label = tk.Label(image=image)
            label.photo = image
            label.grid(row=i+1, column=1)
            all_lebels.append(label)


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
        """Use openweathermap.org to get current weather in city
        Return content of response"""
        API_KEY = self.read_api()
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city, API_KEY)
        r = requests.get(url)
        #content = r.text
        content_json = r.json()
        return (content_json)

    def my_weather_forecast(self, city):
        """Use openweathermap.org to get weather forecast in city
                Return content of response"""
        API_KEY = self.read_api()
        url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}'.format(city, API_KEY)
        r = requests.get(url)
        content_json = r.json()
        print(content_json)
        return (content_json)


    def get_temperature(self, value):
        """Determine temperature from weather"""
        ORDER = 2
        try:
            temp_data_in_K = self.weather['main'][value]
            temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
            return temp_data_in_C
        except Exception as ex:
            messagebox.showinfo(title='Error', message='Got data error')
            print('Входные данные вызвали ошибку ', type(ex))
            return "\nНе удалось узнать {}".format(value)

    def get_temperature_forecast(self):
        """Определяем прогноз погоды на два дня вперед в 15:00 и 21:00, скачиваем иконки, обновляем текст в окне
        Иконки обновляются в функции weather_info"""
        ORDER = 2
        day_temperature_list, evening_temperature_list = [], []
        day_feel_temperature_list, evening_feel_temperature_list = [], []
        tomorrow = str(self.weather_forecast['list'][8]['dt_txt']).split()[0]  # Дата завтрашнего дня, убираем часы мин
        day_after_tomorrow = str(self.weather_forecast['list'][16]['dt_txt']).split()[0]  # Дата послезавтра
        days = [tomorrow, day_after_tomorrow]
        try:
            counter = 0
            for i in range(len(self.weather_forecast['list'])):
                if '15:00:00' in self.weather_forecast['list'][i]['dt_txt']:
                    if self.current_data not in self.weather_forecast['list'][i]['dt_txt'] and counter < 2:
                        temp_data_in_K = self.weather_forecast['list'][i]['main']['temp']
                        temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
                        day_temperature_list.append(temp_data_in_C)

                        temp_data_in_K = self.weather_forecast['list'][i]['main']['feels_like']
                        temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
                        day_feel_temperature_list.append(temp_data_in_C)

                        ico_name = self.weather_forecast['list'][i]['weather'][0]['icon']
                        ico_url = "https://openweathermap.org/img/wn/%s.png" % ico_name
                        response = requests.get(ico_url)
                        img = Image.open(BytesIO(response.content))
                        img.save('day{}.png'.format(counter))
                        counter += 1
            counter = 0
            for i in range(len(self.weather_forecast['list'])):
                if '21:00:00' in self.weather_forecast['list'][i]['dt_txt']:
                    if self.current_data not in self.weather_forecast['list'][i]['dt_txt'] and counter < 2:
                        temp_data_in_K = self.weather_forecast['list'][i]['main']['temp']
                        temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
                        evening_temperature_list.append(temp_data_in_C)

                        temp_data_in_K = self.weather_forecast['list'][i]['main']['feels_like']
                        temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
                        evening_feel_temperature_list.append(temp_data_in_C)

                        ico_name = self.weather_forecast['list'][i]['weather'][0]['icon']
                        ico_url = "https://openweathermap.org/img/wn/%s.png" % ico_name
                        response = requests.get(ico_url)
                        img = Image.open(BytesIO(response.content))
                        img.save('evening{}.png'.format(counter))
                        counter += 1
            # return temperature_list
            for i in range(2):
                weather_data_day = tk.Label(
                    self.window,
                    text='{} day temperature is {} C, feels like {} C'.format(days[i],
                                                                                 day_temperature_list[i],
                                                                                 day_feel_temperature_list[i]),
                    font=('Times New Roman', 18), justify='left')
                weather_data_day.grid(column=0, row=2*i+2, sticky='w')

                weather_data_evening = tk.Label(
                    self.window,
                    text='{} evening temperature is {} C, feels like {} C'.format(days[i],
                                                                              evening_temperature_list[i],
                                                                              evening_feel_temperature_list[i]),
                    font=('Times New Roman', 18), justify='left')
                weather_data_evening.grid(column=0, row=2*i+3, sticky='w')

        except Exception as ex:
            messagebox.showinfo(title='Error', message='Got data error')


    def get_ico(self):
        """Скачиваем иконку для текущей погоды"""
        try:
            ico_name = self.weather['weather'][0]['icon']
            ico_url = "https://openweathermap.org/img/wn/%s.png" % ico_name
            response = requests.get(ico_url)
            img = Image.open(BytesIO(response.content))
            img.save('test.png')
        except:
            messagebox.showinfo(title='Error', message='Image download error')

    def get_current_data(self):
        """Определяем какое сегодня число и выводим год-месяц-день"""
        data = str(datetime.datetime.now()).split()
        data = data[0]
        return data

    def create_temp(self):
        """Создаем директорию для временных файлов и переходим в нее"""
        try:
            os.mkdir('Temp')
        except:
            pass
        try:
            shutil.copy2('API.txt', 'Temp')
        except:
            pass
        os.chdir('Temp')

if __name__ == '__main__':
    app = App()

