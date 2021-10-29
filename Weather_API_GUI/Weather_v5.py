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
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np


class App:
    def __init__(self):
        # Создаем папку Temp для временных файлов
        self.create_temp()

        # Узнаем имя пользователя
        name = os.getlogin()

        # Костыль, задаем количеством строчек Label + 1(картинка температуры): используется для их обновления
        self.num_label = 11

        # Узнаем местоположение пользователя
        self.city = self.user_location()

        # Получаем базу городов России
        self.city_base = self.city_list()

        # Узнаем текущую дату в формате год-месяц-число
        self.current_data = self.get_current_data()

        # Создаем рабочую область и настриваем оформление
        self.window = tk.Tk()
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        style.map('TCombobox', selectbackground=[('readonly', 'none')])
        style.map('TCombobox', selectforeground=[('readonly', 'black')])
        self.window.title("Weather forecast")
        w_height, w_width = 660, 775
        self.window.geometry('{}x{}'.format(w_height, w_width))
        self.window.resizable(False, False)  # Запрещаем менять размер окна
        self.bg_color = '#D0F0C0'  # Выбираем цвет фона
        self.font = 'Comic Sans MS'
        self.font_size = 16
        self.window['bg'] = self.bg_color

        # Централизуем положения окна. Набор стандартных инструкций из интернета
        self.window.withdraw()
        self.window.update_idletasks()  # Update "requested size" from geometry manager
        x = (self.window.winfo_screenwidth() - w_width) / 2
        y = (self.window.winfo_screenheight() - w_height) / 2
        self.window.wm_geometry("+%d+%d" % (x, y))
        self.window.deiconify()

        # Пример загрузки готовой темы
        # self.window.tk.call("source", "sun-valley.tcl")
        # self.window.tk.call("set_theme", "light")

        # Уточняем местоположение пользователя
        city_mes = tk.messagebox.askquestion(title='Location',
                                                  message='Hello, {}, are you from {}?'.format(name, self.city))
        # Выбор города ТЕКСТ СЛЕВА ОТ БОКСА ВЫБОРА ГОРОДА
        self.greetings = tk.Label(self.window,
                                  text='Select city:',
                                  font=(self.font, self.font_size),
                                  justify='left', width=9, bg=self.bg_color)
        self.greetings.grid(column=0, row=0, sticky='w')

        # Получаем список городов России и добавляем текущий город в общий список
        self.city_list = self.city_list()
        self.city_list.append(self.city)

        # Создаем БОКС ВЫБОРА ГОРОДА
        self.city_box = Combobox(self.window, values=self.city_list,
                                 state='readonly', font=(self.font, 20),
                                 justify='left', background='white', foreground="black")

        # Обработка диалогового окна Location
        if city_mes == 'yes':
            self.city_box.current(len(self.city_list) - 1)
            self.weather_info()
        if city_mes == 'no':
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

    def weather_info(self, event=None):
        """Обновляет информацию о погоде"""
        self.city = self.city_box.get()
        self.weather = self.my_weather_forecast(forecast=False, city=self.city)  # Текущая погода
        self.weather_forecast = self.my_weather_forecast(forecast=True, city=self.city)  # Прогноз погоды
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
            text='Now temperature is {}° C, feels like {}° C'.format(self.temperature,
                                                                         self.real_temperature),
            font=(self.font, self.font_size), justify='left', bg=self.bg_color)
        weather_data.grid(column=0, row=1, sticky='w')

        # Обрабатываем прогноз погоды, выводим текст прогноза
        self.get_temperature_forecast()

        # Тест графика
        self.plot()

        # Отображаем иконки погоды
        img_list = ['test.png', 'day0.png', 'evening0.png', 'day1.png', 'evening1.png', 'plt.png']
        all_lebels = []  # Используется чтобы коллектор мусора пайтона не убирал из памяти иконки погоды
        for i in range(len(img_list)):
            image = ImageTk.PhotoImage(Image.open(img_list[i]))

            if 'plt' not in img_list[i]:
                label = tk.Label(image=image, justify='right', bg=self.bg_color)
                label.photo = image
                label.grid(row=i + 1, column=1)
            else:
                label = tk.Label(image=image, justify='left', bg=self.bg_color)
                label.photo = image
                label.grid(row=15, columnspan=2)
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
        except FileNotFoundError:
            url = 'https://on55.ru/articles/2'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find_all('td')
            for i in range(5, len(items)):
                if i % 5 == 0:
                    city_base.append(items[i].get_text())
            with open('city_base.txt', 'w') as w:
                for city in city_base:
                    if 'Оспаривается' not in city:
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

    def my_weather_forecast(self, forecast, city):
        """Use openweathermap.org to get current weather and weather forecast in city
                Return content of response"""
        API_KEY = self.read_api()
        if forecast:
            url = 'https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}'.format(city, API_KEY)
        else:
            url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city, API_KEY)
        r = requests.get(url)
        content_json = r.json()
        return (content_json)

    def get_temperature(self, value):
        """Determine temperature from weather"""
        ORDER = 1
        try:
            temp_data_in_K = self.weather['main'][value]
            temp_data_in_C = round((temp_data_in_K - 273.15), ORDER)
            return temp_data_in_C
        except Exception as ex:
            messagebox.showinfo(title='Error', message='Got data error: \n {}: {}'.format(ex.__class__, ex))

    def get_temperature_forecast(self):
        """Определяем прогноз погоды на два дня вперед в 15:00 и 21:00, скачиваем иконки, обновляем текст в окне
        Иконки обновляются в функции weather_info"""
        ORDER = 1
        day_temperature_list, evening_temperature_list = [], []
        day_feel_temperature_list, evening_feel_temperature_list = [], []
        tomorrow = str(self.weather_forecast['list'][8]['dt_txt']).split()[0]  # Дата завтрашнего дня, убираем часы мин
        day_after_tomorrow = str(self.weather_forecast['list'][16]['dt_txt']).split()[0]  # Дата послезавтра
        days = [tomorrow, day_after_tomorrow]
        self.all_data = []
        self.all_temp = []
        self.all_real_temp = []
        determine_start_time = True
        try:
            counter = 0
            for i in range(len(self.weather_forecast['list'])):
                self.all_data.append(self.weather_forecast['list'][i]['dt_txt'])
                self.all_temp.append(round((self.weather_forecast['list'][i]['main']['temp'] - 273.15), ORDER))
                self.all_real_temp.append(round((self.weather_forecast['list'][i]['main']['feels_like'] - 273.15), ORDER))
                if '00:00:00' in self.weather_forecast['list'][i]['dt_txt'] and \
                        self.current_data not in self.weather_forecast['list'][i]['dt_txt']:
                    if determine_start_time:
                        self.start_time = i  # Определяем положение времени 00:00:00 следующего дня для графика
                        determine_start_time = False
                    self.end_time = i

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
                    text='{} day temperature is {}° C, feels like {}° C'.format(days[i],
                                                                              day_temperature_list[i],
                                                                              day_feel_temperature_list[i]),
                    font=(self.font, self.font_size), justify='left',bg=self.bg_color)
                weather_data_day.grid(column=0, row=2 * i + 2, sticky='w')

                weather_data_evening = tk.Label(
                    self.window,
                    text='{} evening temperature is {}° C, feels like {}° C'.format(days[i],
                                                                                  evening_temperature_list[i],
                                                                                  evening_feel_temperature_list[i]),
                    font=(self.font, self.font_size), justify='left', bg=self.bg_color)
                weather_data_evening.grid(column=0, row=2 * i + 3, sticky='w')

        except Exception as ex:
            messagebox.showinfo(title='Error', message='Got data error: \n {}: {}'.format(ex.__class__, ex))

    def get_ico(self):
        """Скачиваем иконку для текущей погоды"""
        try:
            ico_name = self.weather['weather'][0]['icon']
            ico_url = "https://openweathermap.org/img/wn/%s.png" % ico_name
            response = requests.get(ico_url)
            img = Image.open(BytesIO(response.content))
            img.save('test.png')
        except Exception as ex:
            messagebox.showinfo(title='Error', message='Got data error: \n {}: {}'.format(ex.__class__, ex))

    def get_current_data(self):
        """Определяем какое сегодня число и выводим год-месяц-день"""
        data = str(datetime.datetime.now()).split()
        data = data[0]
        return data

    def create_temp(self):
        """Создаем директорию для временных файлов и переходим в нее"""
        try:
            os.mkdir('Temp')
        except FileExistsError:
            pass
        try:
            shutil.copy2('API.txt', 'Temp')
        except FileNotFoundError:
            pass

        os.chdir('Temp')

    def funcForFormatter(self, x, pos):
        date_list_night = np.arange(self.start_time,self.end_time,8)  # 5,38,8
        date_list_day = np.arange(self.start_time+4,self.end_time,8)  # 9,38,8
        x = int(x)

        if x in date_list_night:
            date = str(self.all_data[x]).split()
            return u'{}\n{}'.format(date[0][5:],date[1][:-3])  # Используем срез, чтобы обрезать год и секунды

        if x in date_list_day:
            date = str(self.all_data[x]).split()
            return u'{}\n{}'.format(date[0][5:],date[1][:-3])  # Используем срез, чтобы обрезать год и секунды


    def plot(self):
        fig = plt.figure(figsize=(6.6, 4.8), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.bg_color)
        ax.patch.set_facecolor(self.bg_color)
        xdata = np.arange(0,len(self.all_data),1)
        xmin, xmax = xdata[self.start_time], xdata[self.end_time]  # удаляем прогнозы на текущий день и на начало 5-го дня
        ymin, ymax = min(self.all_real_temp), max(self.all_temp)

        # Создаем форматер
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        """Информация о FuncFormatter: позволяет гибко настраивать формат меток с помощью функции, 
        которая будет возвращать строковое представление каждой метки"""
        formatter = matplotlib.ticker.FuncFormatter(self.funcForFormatter)

        # Установка форматера для оси X
        ax.xaxis.set_major_formatter(formatter)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_title("Four day weather forecast", fontsize=14, color='black', font=self.font)
        ax.set_ylabel("Temperature, [°C]", fontsize=14, color='black')

        for i in np.arange(self.start_time,self.end_time,8):  # 38
            ax.vlines(i, ymin, ymax, color='black')
        for i in np.arange(self.start_time+4,self.end_time,8):  # 34
            ax.vlines(i, ymin, ymax, color='black', linestyles='--')
        ax.plot(xdata, self.all_temp, label = '$T$', color = 'red')
        ax.plot(xdata, self.all_real_temp, label ='$T_{feel}$', color = '#0F27FF')
        plt.legend()
        plt.savefig('plt.png')
        plt.close()


if __name__ == '__main__':
    app = App()
