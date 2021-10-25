import PySimpleGUI as sg
import os
import time
import math

sg.theme('LightBlue2')
# sg.theme_previewer()

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

frame_layout_press = [
    [sg.Checkbox(text="Уравнение Николаса", tooltip="Аналитическое уравнение для определения давления в жидкости\n"
                                                    "Небходимо задать rho и T", default=True, key='_Nicolas_'),
     sg.Checkbox(text="Уравнение Джонсона", tooltip="Аналитическое уравнение для определения давления в жидкости\n"
                                                    "Небходимо задать rho и T", default=True, key='_Jonson_'),
     sg.Checkbox(text="Уравнение Вассермана", tooltip="Эмпирическое уравнение для определения давления в жидкости",
                 default=True, key='_Vasserman_'),
     sg.Checkbox(text='P_MD', tooltip='Давление, рассчитанное методом МД без учета поправки', default=True,
                 key='_P_MD_'),
     sg.Checkbox(text='P_MD_full', tooltip='Давление рассчитанное методом МД с учетом поправки', default=True,
                 key='_P_MD_full_'),
     sg.Checkbox(text='P_LRC', tooltip='Величина поправки в давление', default=False, key='_P_LRC_', visible=False)],
    [sg.Checkbox(text='Out_in_reduced', tooltip='Вывод данных в безразмерном виде', default=True,
                 key='_Out_in_reduced_', visible=False),
     sg.Checkbox(text='Out_in_dim', tooltip='Вывод данных в размерном виде', default=True, key='_Out_in_dim_',
                 visible=False),
     sg.Checkbox(text="Reduced", tooltip="В режиме Reduced нужно вводить безразмерные величины", default=True,
                 key='_Reduced_'),
     sg.Checkbox(text='Print input_dat', tooltip='Вывод входных данных', default=True, key='_Print_input_dat_'),
     sg.Checkbox(text='Print_input_mod', tooltip='Дублировать входные величины в размерном/безразмерном виде',
                 default=True, key='_Print_input_mod_', visible=False),
     sg.Checkbox(text='Difference in results', tooltip='Вывод разницы между аналитическим, эмпирическим уравнениями и '
                                                       'результатом расчета методом МД', default=True,
                 key='_Difference_', visible=False)],
    [sg.Text('Порядок округления = ', tooltip='Кол-во знаков в дробной части'),
     sg.InputText(size=(6, 2), default_text=4, key="_Round_order_"),
     sg.Text('Кол-во чанков = ', tooltip='Количество подобластей в симулируемой ячейке'),
     sg.InputText(size=(6, 2), default_text=100, key="_Nchunks_"),
     sg.Text('Объем чанка = ', tooltip='Объем одной подобласти расчета в [А^3]'),
     sg.InputText(size=(10, 2), default_text=65000, key="_Vchunks_"),
     sg.Button(button_text='Применить')]
]

frame_layout_density = [
    [sg.Checkbox(text="Уравнение Гилгена(Ж)", tooltip="Эмпирическое уравнение для определения плотности жидкого аргона\n"
                                                    "Небходимо задать rho, T, T_c, P_c", default=True,
                 key='_Gilgen_rho_liq_')]
]

Press_tab_layout = [
    [sg.Text('Input_file  '), sg.InputText(default_text='/home/igor/lammps/src/pp.dat', key='_input_file_'),
     sg.FileBrowse(),
     sg.Checkbox(text='Использовать входной файл',tooltip='Необходимо задать входной файл, чтобы функции '
                                                          'P_MD и P_MD_full были активны',
                 default=True, key='_Check_input_file_')],
    [sg.Text('Output_dir', tooltip='Определить директорию для выходных  файлов'), sg.InputText(
        default_text='/home/igor/lammps/src/', key='_output_dir_'), sg.FileBrowse()],
    [sg.Frame("Параметры расчета:", frame_layout_press, title_color='blue')],
    [sg.Text('T* = ', tooltip='Температура, [K]', key='_Text_T_'),
     sg.InputText(size=(10, 2), key='_T_', default_text='0.9203'),

     sg.Text('rho* = ', tooltip="Плотность, [g/cm^3]", key='_Text_rho_'),
     sg.InputText(size=(10, 2), key="_rho_", default_text='0.9'),

     sg.Text('R_c* = ', tooltip="Радиус обрезания действия потенциала ЛД, [A]", key='_Text_R_c_'),
     sg.InputText(size=(10, 2),default_text=2.5,key="_R_c_"),

     sg.Text("T_c* = ", tooltip="Критическая температура, [K]", key='_Text_T_c_'),
     sg.InputText(size=(10, 2), default_text=1.2607,key='_T_c_', readonly=False),

     sg.Text("P_c* = ", tooltip="Критическое давление, [МПа]", key='_Text_P_c_'),
     sg.InputText(size=(10, 2), default_text=0.0116,key="_P_c_", readonly=True)],

    [sg.Text('Epsilon = ', tooltip='Энергия связи, [eV]\nЕё величина не зависит от режима Reduced'),
     sg.InputText(size=(10, 2), default_text=0.104, key="_Epsilon_"),
     sg.Text('Sigma = ', tooltip='Длина связи, [A]\nЕё величина не зависит от режима Reduced'),
     sg.InputText(size=(10, 2), default_text=3.4, key="_Sigma_")],
    [sg.Output(size=(100, 20), key='_Output_')],
    [sg.Submit(button_text='Calculate'), sg.Button(button_text='Clear'), sg.Button(button_text='Info')],
    [sg.Exit('Exit')]
]

Density_tab_layout = [
    [sg.Text('T = ', tooltip='Температура, [K]'), sg.InputText(size=(10, 2))]
]

layout = [
    [sg.TabGroup([[sg.Tab('Pressure', Press_tab_layout), sg.Tab('Density', Density_tab_layout)]]), ]
]
window = sg.Window('Thermodynamic parameters calculator', layout)

Pscale = 419.819865662528  # умножить на Pscale, чтобы получить размерную величину давления в [бар]
Tscale = 119.52653665398  # умножить на Tscale, чтобы получить размерную величину температуры в [K]
Rhoscale = 1.6877919550173  # умножить на Rhoscale, чтобы получить размерную величину плотности в [г/см^3]
k_B = 1.38 * 10 ** (-23)
round_order = 4
status = 'Reduced'
sys_ave_press = 0


def to_float(T, rho, R_c, T_c, P_c, Epsilon, Sigma):
    values['_T_'] = float(T)
    values['_rho_'] = float(rho)
    values["_R_c_"] = float(R_c)
    values['_T_c_'] = float(T_c)
    values['_P_c_'] = float(P_c)
    values["_Epsilon_"] = float(Epsilon)
    values["_Sigma_"] = float(Sigma)
    return values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'], values["_Epsilon_"], \
           values["_Sigma_"]

def update_value(status, T, rho, R_c, T_c, P_c):
    if status == 'Reduced':
        window.FindElement('_Text_T_').Update('T* = ')
        window.FindElement('_Text_rho_').Update('rho* = ')
        window.FindElement('_Text_R_c_').Update('R_c* = ')
        window.FindElement('_Text_T_c_').Update('T_c* = ')
        window.FindElement('_Text_P_c_').Update('P_c* = ')
    if status == 'Dim':
        window.FindElement('_Text_T_').Update('T = ')
        window.FindElement('_Text_rho_').Update('rho = ')
        window.FindElement('_Text_R_c_').Update('R_c = ')
        window.FindElement('_Text_T_c_').Update('T_c = ')
        window.FindElement('_Text_P_c_').Update('P_c = ')
    window.FindElement('_T_').Update(T)
    window.FindElement('_rho_').Update(rho)
    window.FindElement('_R_c_').Update(R_c)
    window.FindElement('_T_c_').Update(T_c)
    window.FindElement('_P_c_').Update(P_c)

def to_reduced(T, rho, R_c, T_c, P_c):
    values['_T_'] = round((T / Tscale), round_order)
    values['_rho_'] = round((rho / Rhoscale), round_order)
    values["_R_c_"] = round((R_c / values['_Sigma_']), round_order)
    values['_T_c_'] = round((T_c / Tscale), round_order)
    values['_P_c_'] = round((P_c / Pscale), round_order)
    return values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_']

def to_dim(T, rho, R_c, T_c, P_c):
    values['_T_'] = round((T * Tscale), round_order)
    values['_rho_'] = round((rho * Rhoscale), round_order)
    values["_R_c_"] = round((R_c * float(values['_Sigma_'])), round_order)
    values['_T_c_'] = round((T_c * Tscale), round_order)
    values['_P_c_'] = round((P_c * Pscale), round_order)
    return values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_']

def T_to_reduced(T):
    values['_T_'] = T / Tscale
    return values['_T_']

def T_to_dim(T):
    values['_T_'] = T * Tscale
    return values['_T_']

def rho_to_reduced(rho):
    values['_rho_'] = rho / Rhoscale
    return values['_rho_']

def rho_to_dim(rho):
    values['_rho_'] = rho * Rhoscale
    return values['_rho_']

def R_c_to_reduced(R_c):
    values['_R_c_'] = R_c / values['_Sigma_']
    return values['_R_c_']

def R_c_to_dim(R_c):
    values['_R_c_'] = R_c * values['_Sigma_']
    return values['_R_c_']




def print_input_dat(reduced, T, rho, R_c, T_c, P_c):
    if reduced == True:
        print("\nИспользованы следующие входные безразмерные величины:")
        print('T* = {}    rho* = {}    R_c* = {}*sigma,    T_c* = {},    P_c* = {}'.format(T, rho, R_c, T_c, P_c))
        print("Их значения в размерном виде:")
        to_dim(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        print('T = {} [K]    rho = {} [г/см^3]    R_c = {} [A],    T_c = {} [K],    P_c = {} [МПа]'.format(
            values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_']))
        to_reduced(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        print('')
    else:
        print("\nИспользованы следующие входные размерные величины:")
        print('T = {} [K]    rho = {} [г/см^3]    R_c = {} [A],    T_c = {} [K],    P_c = {} [Мпа]'.format(
            values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_']))
        print("Их значения в безразмерном виде:")
        to_reduced(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        print('T* = {}    rho* = {}    R_c* = {}*sigma,    T_c* = {},    P_c* = {}'.format(
            values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_']))
        to_dim(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        print('')

def P_LRC(rho, r_c, Round_order):
    round_order = int(Round_order)
    U_tail = (8 / 3) * math.pi * rho * ((1 / 3) * (1 / r_c) ** 9 - (1 / r_c) ** 3)
    P_LRC = (32 / 9) * math.pi * rho ** 2 * (r_c ** -9) - (16 / 3) * math.pi * rho ** 2 * (r_c ** -3)
    """print("Поправка к потенциальной энергии U*_tail = {} = {} [eV] \n"
          "Поправка к давлению P*_LRC = {} = {} [bars]".format(round(U_tail, round_order), round((U_tail / 0.0104), round_order),
                                                               round(P_LRC, round_order), round((P_LRC * Pscale), round_order)))"""
    print("Поправка к давлению P*_LRC = {} = {} [bars]".format(round(P_LRC, round_order),
                                                               round((P_LRC * Pscale), round_order)))
    return P_LRC * Pscale

def Nicolas_pressure(T_r, rho_r, Round_order):
    round_order = int(Round_order)
    gamma = 3
    x = (
    -0.044480725, 7.2738221, -14.343368000000002, 3.8397096, -2.0057745, 1.9084472, -5.7441787, 25.110073, -4523.2787,
    0.008932716200000001, 9.816335800000001, -61.434571999999996, 14.161454, 43.353840999999996, 1107.8327, -35.429519,
    10.591298, 497.70046, -353.38542, 4503.6093, 7.7805296, 13567.114, -8.5818023, 16646.578, -14.092234000000001,
    19386.911, 38.585868, 3380.0371, -185.67754, 8487.4693, 97.508689, -14.48306
    )

    P_r = (rho_r * T_r + rho_r ** 2 * (x[0] * T_r + x[1] * T_r ** (1 / 2) + x[2] + x[3] * T_r ** (-1) + x[4] * T_r ** (-2)) +
           rho_r ** 3 * (x[5] * T_r + x[6] + x[7] * T_r ** (-1) + x[8] * T_r ** (-2)) +
           rho_r ** 4 * (x[9] * T_r + x[10] + x[11] * T_r ** (-1)) +
           rho_r ** 5 * (x[12]) +
           rho_r ** 6 * (x[13] * T_r ** (-1) + x[14] * T_r ** (-2)) +
           rho_r ** 7 * (x[15] * T_r ** (-1)) +
           rho_r ** 8 * (x[16] * T_r ** (-1) + x[17] * T_r ** (-2)) +
           rho_r ** 9 * (x[18] * T_r ** (-2)) +
           rho_r ** 3 * (x[19] * T_r ** (-2) + x[20] * T_r ** (-3)) * math.exp(-gamma * rho_r ** 2) +
           rho_r ** 5 * (x[21] * T_r ** (-2) + x[22] * T_r ** (-4)) * math.exp(-gamma * rho_r ** 2) +
           rho_r ** 7 * (x[23] * T_r ** (-2) + x[24] * T_r ** (-3)) * math.exp(-gamma * rho_r ** 2) +
           rho_r ** 9 * (x[25] * T_r ** (-2) + x[26] * T_r ** (-4)) * math.exp(-gamma * rho_r ** 2) +
           rho_r ** 11 * (x[27] * T_r ** (-2) + x[28] * T_r ** (-3)) * math.exp(-gamma * rho_r ** 2) +
           rho_r ** 13 * (x[29] * T_r ** (-2) + x[30] * T_r ** (-3) + x[31] * T_r ** (-4)) * math.exp(
                -gamma * rho_r ** 2)
           )
    P_r = round(P_r, round_order)
    P_Nicloas = round((P_r * Pscale), round_order)
    print("Давление в жидкости по ур. Николаса: P* = {},   P = {} [бар]".format(P_r, P_Nicloas))

def Jonson_pressure(T_r, rho_r, Round_order):
    round_order = int(Round_order)
    gamma = 3
    Sum_a_mul_rho, Sum_b_mul_rho = 0, 0
    x = (
        0.8623085097507421, 2.976218765822098, -8.402230115796038, 0.1054136629203555, -0.8564583828174598,
        1.582759470107601, 0.7639421948305453, 1.753173414312048, 2798.291772190376, -0.048394220260857657,
        0.9963265197721935, -36.98000291272493, 20.84012299434647, 83.05402124717285, -957.4799715203068,
        -147.7746229234994, 63.98607852471505, 16.03993673294834, 68.05916615864377, -2791.293578795945,
        -6.245128304568454, -8116.836104958410, 14.88735559561229, -10593.46754655084, -113.1607632802822,
        -8867.771540418822, -39.86982844450543, -4689.270299917261, 259.3535277438717, -2694.523589434903,
        -721.8487631550215, 172.1802063863269
    )
    a = (
        x[0] * T_r + x[1] * (T_r ** (1/2)) + x[2] + x[3] / T_r + x[4] / (T_r ** 2),
        x[5] * T_r + x[6] + x[7] / T_r + x[8] / (T_r ** 2),
        x[9] * T_r + x[10] + x[11] / T_r,
        x[12],
        x[13] / T_r + x[14] / (T_r ** 2),
        x[15] / T_r,
        x[16] / T_r + x[17] / (T_r ** 2),
        x[18] / (T_r ** 2)
    )
    b = (
        x[19] / (T_r ** 2) + x[20] / (T_r ** 3),
        x[21] / (T_r ** 2) + x[22] / (T_r ** 4),
        x[23] / (T_r ** 2) + x[24] / (T_r ** 3),
        x[25] / (T_r ** 2) + x[26] / (T_r ** 4),
        x[27] / (T_r ** 2) + x[28] / (T_r ** 3),
        x[29] / (T_r ** 2) + x[30] / (T_r ** 3) + x[31] / (T_r ** 4)
    )
    F = math.exp(-gamma * (rho_r ** 2))
    for i in range(1,9):
        Sum_a_mul_rho += a[i-1] * (rho_r ** (i + 1))
    for i in range(1,7):
        Sum_b_mul_rho += b[i-1] * (rho_r ** (2*i + 1))

    P_r = rho_r * T_r + Sum_a_mul_rho + F * Sum_b_mul_rho
    P_dim = P_r * Pscale
    print("Давление в жидкости по ур. Джонсона: P* = {},   P = {} [бар]".format(round(P_r, round_order),
                                                                                round(P_dim, round_order)))

def Vasserman_pressure(T, rho, Round_order):
    round_order = int(Round_order)
    P_Liq_by_Vasserman = ((-456.6 + 4.157 * T + 4274 * (10 ** 2) * (T ** -2) - 360553 * (10 ** 4) * (T ** -4)) *
                          (rho ** 2) - (733.5 - 2.67 * T) * (rho ** 4) + 287 * (rho ** 6))
    P_Liq_by_Vasserman = round(P_Liq_by_Vasserman, round_order)
    P_Liq_by_Vasserman_r = round((P_Liq_by_Vasserman / Pscale), round_order)
    print('Давление в жидкости по ур. Вассермана: P* = {}, P = {} [бар]'.format(P_Liq_by_Vasserman_r, P_Liq_by_Vasserman))

def create_output(*args):  # объявляем функцию, *args -- позволяет задать любое кол-во аргументов функции
    with open(args[0] + "Press_py.dat", "w") as f:  # Создаем пустой файл для выходных данных и записываем 4 столбца.
        f.write('Chunk_num Ncount v_pp Chunk_press \n')  # v_pp -- давление на один атом в чанке
    f.close()
    with open(args[0] + "Press_prof_py.dat", "w") as p:  # Создаем dat для gnuplot
        p.write('Chunk_num Chunk_press_NkT Chunk_press \n')
    p.close()

def MD_pressure(file,dir, Round_order):  # функция, которая обрабатывает выходной файл по строчкам
    round_order = int(Round_order)
    i, k, sum_pressL1, sum_pressG, sum_pressL2, sys_ave_press = 0, 0, 0, 0, 0, 0
    sum_pressL1_NkT, sum_pressG_NkT, sum_pressL2_NkT, sys_ave_press_NkT = 0, 0, 0, 0
    avepress_L1, avepress_G, avepress_L2 = 0, 0, 0
    l = 2  # Кол-во нижних и верхних чанков, которые не рассматриваем при расчете давления.
    chunk_volume = 65000 * 10 ** (-30) # в [м^3]
    with open(file, 'r+') as z:  # Открываем выходной файл lammps
        new_string = z.readline()
        while new_string:  # Читаем по строчке до тех пор, пока не получим пустую строчку, тогда false и выход из цикла
            new_string = z.readline()
            try:
                if new_string[0] == '#':  # Пропускаем комментарии
                    pass
                else:
                    new_string = new_string.split(' ')  # Превращаем строчку в список
                    len_new_string = len(new_string)  # Определяем длину списка

                    if len_new_string == 3:
                        i, sum_pressL1, sum_pressG, sum_pressL2 = 0, 0, 0, 0
                        with open(dir + "Press_py.dat", "a") as a:
                            new_string = new_string[0] + ' ' + new_string[1] + ' ' + new_string[2] + '\n'
                            a.write(new_string)

                        with open(dir + "Press_prof_py.dat", "a") as a:
                            new_string = new_string[0] + ' ' + new_string[1] + ' ' + new_string[2] + '\n'
                            a.write(new_string)

                    if len_new_string == 9:
                        press_atom = float(new_string[-2].replace('\n', ''))  # среднее давление на один атом в чанке
                        Ncount = float(new_string[-3])  # среднее кол-во частиц в чанке
                        temp = float(new_string[-1])  # температура в чанке с учетом гидродин ск-ти
                        press_chunk = str(press_atom * Ncount)  # среднее давление в чанке с учетом вириала
                        press_chunk += '\n'  # добавляем символ переноса строки
                        chunk_number = new_string[2]
                        press_chunk_NkT = (Ncount * k_B * temp / chunk_volume) * 10 ** (
                            -5)  # Давление по формуле NkT/V в [бар]
                        # print(press_chunk_NkT, Ncount,temp)
                        i += 1
                        if l < i <= 20:
                            sum_pressL1 += float(press_chunk.replace('\n', ''))
                            sum_pressL1_NkT += press_chunk_NkT
                        elif 20 < i <= 79:
                            sum_pressG += float(press_chunk.replace('\n', ''))
                            sum_pressG_NkT += press_chunk_NkT
                        elif 80 < i <= 100 - l:
                            sum_pressL2 += float(press_chunk.replace('\n', ''))
                            sum_pressL2_NkT += press_chunk_NkT

                        if i == 100:
                            sum_pressL1 = sum_pressL1 / (20 - l)
                            sum_pressG = sum_pressG / (60)
                            sum_pressL2 = sum_pressL2 / (20 - l)
                            avepress = (sum_pressL1 + sum_pressL2 + sum_pressG) / 3
                            sum_pressL1_NkT = sum_pressL1_NkT / (20 - l)
                            sum_pressG_NkT = sum_pressG_NkT / (60)
                            sum_pressL2_NkT = sum_pressL2_NkT / (20 - l)
                            avepress_NkT = (sum_pressL1_NkT + sum_pressL2_NkT + sum_pressG_NkT) / 3
                            k += 1
                            if k > 2:  # Первые шаги включают минимизацию, поэтому не рассматриваем их при расчете давления
                                sys_ave_press += avepress  # Суммируем давление всей системы на каждом шаге
                                sys_ave_press_NkT += avepress_NkT  # Суммируем давление всей системы на каждом шаге
                                avepress_L1 += sum_pressL1
                                avepress_G += sum_pressG
                                avepress_L2 += sum_pressL2
                            steps = 'steps: ' + str(k) + '\n'
                            """print('{}NkT/v - W: sum_pressL1 = {} sum_pressG = {} sum_pressL2 = {} avepress = {}'.format(
                                steps,
                                sum_pressL1,
                                sum_pressG,
                                sum_pressL2,
                                avepress))
                            print('NkT: sum_pressL1 = {} sum_pressG = {} sum_pressL2 {} avepress = {}'.format(
                                sum_pressL1_NkT,
                                sum_pressG_NkT,
                                sum_pressL2_NkT,
                                avepress_NkT))"""
                            i, sum_pressL1, sum_pressG, sum_pressL2 = 0, 0, 0, 0
                            sum_pressL1_NkT, sum_pressG_NkT, sum_pressL2_NkT = 0, 0, 0

                        with open(dir + "Press_py.dat", "a") as f:
                            new_string = '{} {} {} {}'.format(chunk_number, Ncount, press_atom, press_chunk)
                            f.write(new_string)

                        with open(dir + "Press_prof_py.dat", "a") as p:  # пишем файл для gnuplot: № чанка и давление в нем
                            new_string = '{} {} {}'.format(chunk_number, press_chunk_NkT, press_chunk)
                            p.write(new_string)
            except IndexError:
                pass
        sys_ave_press_r = round(((sys_ave_press / (k - 2)) / Pscale), round_order)  # Reduced
        sys_ave_press = round((sys_ave_press / (k - 2)), round_order)
        print("Давление рассчитанное методом МД: P*_MD = {},   P_MD = {} [бар]".format(sys_ave_press_r, sys_ave_press))
        z.close()
    return sys_ave_press

while True:
    event, values = window.read()
    # print(event, values)

    if event in (None, 'Exit', 'Cancel'):
        break

    if values['_Reduced_'] == True and event == 'Применить' and status == 'Dim':
        to_float(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'], values["_Epsilon_"],
                 values["_Sigma_"])
        status = 'Reduced'
        to_reduced(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        update_value(status, values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])


    if values['_Reduced_'] == False and event == 'Применить' and status == 'Reduced':
        to_float(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'], values["_Epsilon_"],
                 values["_Sigma_"])
        status = 'Dim'
        to_dim(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])
        update_value(status, values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'])


    if event == 'Clear':
        window.FindElement('_Output_').Update("")


    if event == 'Info':
        print('Здесь когда-нибудь появится информация')

    if event == 'Calculate':

        to_float(values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'], values['_P_c_'], values["_Epsilon_"],
                 values["_Sigma_"])

        if values['_Print_input_dat_']:
            print_input_dat(values['_Reduced_'], values['_T_'], values['_rho_'], values["_R_c_"], values['_T_c_'],
                            values['_P_c_'])

        if values['_P_LRC_']: # Уравнение использует только безразмерные величины: плотность и радиус обрезания
            if values['_Reduced_']:
                P_LRC(values['_rho_'], values['_R_c_'], values["_Round_order_"])
            else:
                rho_to_reduced(values['_rho_'])
                R_c_to_reduced(values['_R_c_'])
                P_LRC(values['_rho_'], values['_R_c_'], values["_Round_order_"])
                rho_to_dim(values['_rho_'])
                R_c_to_dim(values['_R_c_'])

        if values['_Nicolas_']: # Уравнение использует только безразмерные величины: температуру и плотность
            if values['_Reduced_']:
                Nicolas_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])
            else:
                T_to_reduced(values['_T_'])
                rho_to_reduced(values['_rho_'])
                Nicolas_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])
                T_to_dim(values['_T_'])
                rho_to_dim(values['_rho_'])

        if values['_Jonson_']:
            if values['_Reduced_']:
                Jonson_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])
            else:
                T_to_reduced(values['_T_'])
                rho_to_reduced(values['_rho_'])
                Jonson_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])
                T_to_dim(values['_T_'])
                rho_to_dim(values['_rho_'])

        if values['_Vasserman_']:
            if values['_Reduced_']:
                T_to_dim(values['_T_'])
                rho_to_dim(values['_rho_'])
                Vasserman_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])
                T_to_reduced(values['_T_'])
                rho_to_reduced(values['_rho_'])
            else:
                Vasserman_pressure(values['_T_'], values['_rho_'], values["_Round_order_"])

        if values['_P_MD_'] and values['_Check_input_file_']:
            if values['_P_MD_full_']:
                if values['_Reduced_']:
                    p_lrc = P_LRC(values['_rho_'], values['_R_c_'], values["_Round_order_"])
                else:
                    rho_to_reduced(values['_rho_'])
                    R_c_to_reduced(values['_R_c_'])
                    p_lrc = P_LRC(values['_rho_'], values['_R_c_'], values["_Round_order_"])
                    rho_to_dim(values['_rho_'])
                    R_c_to_dim(values['_R_c_'])

                if os.path.exists(values['_input_file_']):
                    create_output(values['_output_dir_'])
                    p_md = MD_pressure(values['_input_file_'], values['_output_dir_'], values["_Round_order_"])
                    print("Давление рассчитанное методом МД с учетом поправки: P_MD_full = {} [бар]".format(
                        round((p_md + p_lrc), int(values["_Round_order_"]))))
                else:
                    print('\n***ОШИБКА***: Неверно указан входной файл, P_MD и P_MD_full не были расчитаны')
            else:
                create_output(values['_output_dir_'])
                MD_pressure(values['_input_file_'], values['_output_dir_'], values["_Round_order_"])


window.close()