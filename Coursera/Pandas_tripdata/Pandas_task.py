import pandas as pd
import numpy as np
import operator
from geopy import distance
import datetime

pd.options.display.max_rows = 100
pd.options.display.max_columns = 100

df = pd.read_csv('201809-citibike-tripdata.csv')
print(df.head(3))
# Найти кол-во строк и столбцов
print(df.shape)

#Найти среднюю длину поездок в минутах(столбец tripduration) c точностью до 2 знака
print(df['tripduration'].describe(include=[np.object]))
print(967.5149/60) # Среднее время поездки

"""
# Вопрос 3
# Сколько поездок начались и закончились в той же самой станции?
sumi = 0
#print(df['start station name'].value_counts())
#print(df['end station name'].value_counts())
for i in range(1, 1877884):
    if df.loc[i, 'start station name'] == df.loc[i, 'end station name']:
        sumi += 1
print('Количество поездок, которые начались и закончились в одной точке: ', sumi) # 41364 -- долго считает, закоментил
"""
df1 = df[df['start station id'] == df['end station id']].value_counts() # сортировка и подсчет
print("Кол-во поездок, к-е закончились и начались в одной и той же точке: \n",df1)

#4 Какой самый используемый байк(bikeid) в городе по количеству поездок?
#print("Самый используемый байк(id): \n",df['bikeid'].value_counts()) # 33875

#5 Найдите идентификатор велосипеда (bikeid), у которого в среднем продолжительность поездок выше, чем у всех остальных
#print("Самая большая продолжительность поездок: \n",df.groupby(['bikeid'])[['tripduration']].mean())
df1 = df.groupby(['bikeid'])['tripduration'].mean()
df1 = sorted(df1.items(), reverse= True, key= lambda x:x[1]) # Сортировка словаря по значениям
print(df1)

# Вопрос 6
# Сколько строк, в которых отсутствуют данные о start station id?
print(len(df[(df['start station id']) == None])) # 0

#Какова средняя продолжительность поездки в минутах в зависимости от типа подписки c точностью до 2 знака?
df1 = df.groupby(['usertype'])[['tripduration']].mean()
#print(df.groupby(['usertype'])[['tripduration']].mean())
print(df1) # Customer: 33.42 min // Subscriber: 13.33


def task8(df):
    # Найдите среднюю длину поездок в километрах с точностью до 2 знака, предварительно выкинув замкнутые траектории(те у которых совпадают start station id = end station id).
    # Hint: можно воспользоваться библиотекой geopy и взять расстояние vincenty(минимальное расстояние между точками)
    df1 = df[df['start station id'] != df['end station id']]  # отфильтровали с одинаковым стартом и концом
    sum = 0
    # print(df1)
    for i in range(0, len(df1) - 1):
        start_point = (df1.iloc[i]['start station latitude'], df1.iloc[i]['start station longitude'])
        end_point = (df1.iloc[i]['end station latitude'], df1.iloc[i]['end station longitude'])
        sum += distance.distance(start_point, end_point).km
        if i % 10000 == 0 and i != 0:
            print('Ave_dist = ', sum / i)

    print('Ave_dist = ', sum / len(df1))

#task8(df)

def task9(df):
    # Вопрос 9 Выберите станцию (start station id) с максимальным количеством отправлений с 18 до 20 вечера включительно
    # Остсортируем строчки с временем отправления от 18:00 до 20:00
    df1 = df[df]

task9(df)





