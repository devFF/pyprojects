import os
import sys
import shutil
import platform
import subprocess
import time
import tabulate
import matplotlib.pyplot as plt

"""
Данная программа запускает основной файл обработки в каждой папке T{}/L{}/Py:
Перед ее запуском необходимо распространить файл обработки run_file в каждую директорию T{}/L{}/Py
Важно чтобы в run_file была активна лишь одна функция
"""

python_dir = sys.executable  # Путь к интерпретатору python3
run_file = 'Data_processing_v9.py'

temperature_folder_list = ['T90']
temperatures_folder_list = ['T90', 'T95', 'T100']
layer_foler_list = ['L100', 'L150', 'L200', 'L250', 'L300', 'L350', 'L400']
thickness_list = [10,15,20,25,30,35,40]
main_dir = os.getcwd()


def run_create_in():
    os.chdir('CREATE_MAIN')
    """Данная функция обновляет каталог Py в каждой директории, также может создавать файлы .in"""
    if "Linux" in platform.system():
        create_in_dir = main_dir + '/CREATE_MAIN/Create_in.py'
    if "Windows" in platform.system():
        create_in_dir = main_dir + '\\CREATE_MAIN\\Create_in.py'
    p = subprocess.Popen([python_dir, create_in_dir])  # Создание процесса запуска Create_in.py
    p.communicate()  # run Create_in.py and wait until finished
    os.chdir(main_dir)


def run_data_processing():
    for t_folder in temperatures_folder_list:
        # os.chdir(os.getcwd() + '\\{}'.format(t_folder))
        for layer in layer_foler_list:
            if "Linux" in platform.system():
                py_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/{}'.format(
                    run_file)  # директория run_file, который нужно запустить
                os.chdir(main_dir + '/{}'.format(t_folder) + '/{}'.format(
                    layer) + '/Py')  # Переход в директорию с файлом run_file
            if "Windows" in platform.system():
                py_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\{}'.format(
                    run_file)  # директория run_file, который нужно запустить
                os.chdir(main_dir + '\\{}'.format(t_folder) + '\\{}'.format(
                    layer) + '\\Py')  # Переход в директорию с файлом run_file
            p = subprocess.Popen([python_dir, py_file_dir])  # Создание процесса запуска run_file
            p.communicate()  # run run_file and wait until finished
            os.chdir(main_dir)  # Переходим в основную директорию


def test_latex():
    head = [r"H, [нм]", "vz, [\mbox{м/c}]", "$\\rho$, $[\mbox{кг}/\mbox{м}^3$]", "J, $[\mbox{кг}/\mbox{м}^2\cdot \mbox{с}]$"]
    table = [35, 120.9, 4.7, 450],[40, 130.1, 4.9, 503]
    print_table = tabulate.tabulate(table, tablefmt='latex_raw', headers=head)
    print_table = print_table.replace('{rrrr}','{|c|c|c|c|}')  # РЕДАКТИРОВАТЬ (кол-во столбцов)  !!!!
    print_table = print_table.replace('\\\n', '\\\n\hline\n').replace('\hline\n\hline','\hline')
    print(print_table)


def latex_vz_density_MF():
    """Считывает текстовые файлы, строит таблицу для LATEX"""
    txt_file = "GAS_vz_dens_MF.txt"
    vz_list, density_list, MF_list = [], [], []
    pressure_list, t_bias_list = [], []
    # Начало блока считывания данных
    for t_folder in temperature_folder_list:
        for layer in layer_foler_list:
            if "Linux" in platform.system():
                txt_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/Txt/{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            if "Windows" in platform.system():
                txt_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\Txt\\{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть

            with open(txt_file_dir, 'r') as r:
                lines = r.readlines()
                for n_line in lines:
                    if n_line.startswith('#'):
                        continue
                    line = n_line.split()
                    vz_list.append(float(line[0]))
                    density_list.append(float(line[1]))
                    MF_list.append(float(line[2]))
                    t_bias_list.append(float(line[3]))
                    pressure_list.append(float(line[4]))
    # Конец блока считывания данных

    #Создание LATEX таблицы
    head = [r"$H$, $[nm]$", "$v_z$, $[m/s]$", "$\\rho$, $[kg/m^3]$",
            "$J$, $[kg/m^2 \cdot s]$", "$T$, $[K]$", "$P$, $[bar]$"]
    table = []
    for i in range(len(vz_list)):
        table.append([])
        table[i] = [thickness_list[i], vz_list[i], density_list[i], MF_list[i], t_bias_list[i], pressure_list[i]]
    print_table = tabulate.tabulate(table, tablefmt='latex_raw', headers=head)
    #print_table = print_table.replace('{rrrr}', '{|c|c|c|c|}')  # РЕДАКТИРОВАТЬ (кол-во столбцов)  !!!!
    print_table = print_table.replace('{r', '{|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|').replace('|r','|c|')
    print_table = print_table.replace('\\\n', '\\\n\hline\n').replace('\hline\n\hline', '\hline')
    print(print_table)


def plot_value_profile(txt_file, N_FIRST_POINT, N_LAST_POINT,
                       title, xlabel, ylabel, fontsize, figsize, dpi, loc, save_name, legend_size):
    """Строит усредненные по 6нс профили температуры_bias, давления, плотности, скорости vz, потока массы для различных значений толщины слоя жидкости"""
    value_list_list = [[], [], [], [], [], [], []]
    coord_list_list = [[], [], [], [], [], [], []]
    # Начало блока считывания данных
    for t_folder in temperature_folder_list:
        for i,layer in enumerate(layer_foler_list):
            if "Linux" in platform.system():
                txt_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/Txt/{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            if "Windows" in platform.system():
                txt_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\Txt\\{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            with open(txt_file_dir, 'r') as r:
                lines = r.readlines()
                for n_line in lines:
                    if n_line.startswith('#'):
                        continue
                    line = n_line.split()
                    coord_list_list[i].append(float(line[0]))
                    value_list_list[i].append(float(line[1]))
    if N_FIRST_POINT > 0:
        for i in range(len(value_list_list)):
            for j in range(N_FIRST_POINT):
                del coord_list_list[i][0]
                del value_list_list[i][0]

    if N_LAST_POINT > 0:
        for i in range(len(value_list_list)):
            for j in range(N_LAST_POINT):
                del coord_list_list[i][-1]
                del value_list_list[i][-1]
    xmin = coord_list_list[0][0]
    xmax = coord_list_list[0][-1]
    plt.figure(figsize=figsize, dpi=dpi)
    plt.title(title, fontsize=fontsize, color='black')
    plt.grid()
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':')
    plt.xlabel(xlabel, fontsize=fontsize, color='black')
    plt.ylabel(ylabel, fontsize=fontsize, color='black')
    plt.xlim(xmin,xmax)
    if N_FIRST_POINT < 10:
        for i in range(len(value_list_list)):
            plt.plot(coord_list_list[i], value_list_list[i], '-', label='H={}[nm]'.format(thickness_list[i]))
    else:
        for i in range(len(value_list_list)):
            plt.plot(coord_list_list[0], value_list_list[i], '-', label='H={}[nm]'.format(thickness_list[i]))
    plt.legend(fontsize=legend_size, loc=loc)
    plt.savefig(save_name)


def plot_all_profiles(legend_size):
    """Функция строит профили макроскопических величин"""
    plot_value_profile(txt_file='profile_massflow.txt', N_FIRST_POINT=2, N_LAST_POINT=2,
                       title='Mass flow profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$J$, $[kg/m^2 \cdot s]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8,6), dpi=80, loc='upper right',
                       save_name="multi_massflow_prof.png")

    plot_value_profile(txt_file='profile_massflow.txt', N_FIRST_POINT=50, N_LAST_POINT=2,
                       title='Mass flow profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$J$, $[kg/m^2 \cdot s]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8,6), dpi=80, loc='center right',
                       save_name="multi_massflow_prof_gas.png")

    plot_value_profile(txt_file='profile_vz.txt', N_FIRST_POINT=2, N_LAST_POINT=2,
                       title='Velocity $v_z$ profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$v_z$, $[m/s]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='lower right',
                       save_name="multi_vz_prof.png")

    plot_value_profile(txt_file='profile_vz.txt', N_FIRST_POINT=50, N_LAST_POINT=2,
                       title='Velocity $v_z$ profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$v_z$, $[m/s]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='lower right',
                       save_name="multi_vz_prof_gas.png")

    plot_value_profile(txt_file='profile_density.txt', N_FIRST_POINT=2, N_LAST_POINT=2,
                       title='Density profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$\\rho$, $[kg/m^3]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='upper right',
                       save_name="multi_density_prof.png")

    plot_value_profile(txt_file='profile_density.txt', N_FIRST_POINT=50, N_LAST_POINT=2,
                       title='Density profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$\\rho$, $[kg/m^3]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='lower right',
                       save_name="multi_density_prof_gas.png")

    plot_value_profile(txt_file='profile_pressure.txt', N_FIRST_POINT=2, N_LAST_POINT=2,
                       title='Pressure profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$P$, $[bar]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='lower right',
                       save_name="multi_press_prof.png")

    plot_value_profile(txt_file='profile_pressure.txt', N_FIRST_POINT=50, N_LAST_POINT=2,
                       title='Pressure profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$P$, $[bar]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='upper right',
                       save_name="multi_press_prof_gas.png")

    plot_value_profile(txt_file='profile_temperature_bias.txt', N_FIRST_POINT=0, N_LAST_POINT=2,
                       title='Temperature profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$T$, $[K]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='upper right',
                       save_name="multi_temperature_bias_prof.png")

    plot_value_profile(txt_file='profile_temperature_bias.txt', N_FIRST_POINT=50, N_LAST_POINT=2,
                       title='Temperature profiles at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                       xlabel='$Z$, $[nm]$',
                       ylabel='$T$, $[K]$',
                       fontsize=15, legend_size=legend_size,
                       figsize=(8, 6), dpi=80, loc='upper right',
                       save_name="multi_temperature_bias_prof_gas.png")


def plot_value_evolution(txt_file, figsize, dpi, loc, title, xlabel, ylabel,legend_size, fontsize, save_name):
    """Строит эволюцию величины для разных значений толщины слоя жидкости"""
    value_list_list = [[], [], [], [], [], [], []]
    time_list = []
    # Начало блока считывания данных
    for t_folder in temperature_folder_list:
        for i,layer in enumerate(layer_foler_list):
            if "Linux" in platform.system():
                txt_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/Txt/{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            if "Windows" in platform.system():
                txt_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\Txt\\{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            with open(txt_file_dir, 'r') as r:
                lines = r.readlines()
                for n_line in lines:
                    if n_line.startswith('#'):
                        continue
                    line = n_line.split()
                    if i == 0:
                        time_list.append(float(line[0]))
                    value_list_list[i].append(float(line[1]))

    plt.figure(figsize=figsize, dpi=dpi)
    plt.title(title, fontsize=fontsize, color='black')
    plt.grid()
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':')
    plt.xlabel(xlabel, fontsize=fontsize, color='black')
    plt.ylabel(ylabel, fontsize=fontsize, color='black')
    plt.xlim(time_list[0], time_list[-1])
    for i in range(len(value_list_list)):
        plt.plot(time_list, value_list_list[i], '-', label = 'H={}[nm]'.format(thickness_list[i]))
    plt.legend(fontsize=legend_size, loc=loc)
    plt.savefig(save_name)


def plot_all_evolutions(legend_size):
    plot_value_evolution(txt_file='press_gas_evolution.txt',
                         title='Gas pressure evolution at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                         xlabel='$t$, $[ns]$',
                         ylabel='$P$, $[bar]$',
                         fontsize=15, legend_size=legend_size,
                         figsize=(8, 6), dpi=80, loc='lower left',
                         save_name="multi_press_gas.png")

    plot_value_evolution(txt_file='t_bias_gas_evolution.txt',
                          title='Gas temperature evolution at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                          xlabel='$t$, $[ns]$',
                          ylabel='$T$, $[K]$',
                          fontsize=15, legend_size=legend_size,
                          figsize=(8, 6), dpi=80, loc='upper right',
                          save_name="multi_t_bias_gas.png")

    plot_value_evolution(txt_file='vz_gas_evolution.txt',
                          title='Gas velocity $v_z$ evolution at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                          xlabel='$t$, $[ns]$',
                          ylabel='$v_z$, $[m/s]$',
                          fontsize=15, legend_size=legend_size,
                          figsize=(8, 6), dpi=80, loc='lower right',
                          save_name="multi_vz_gas.png")

    plot_value_evolution(txt_file='density_gas_evolution.txt',
                          title='Gas density evolution at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                          xlabel='$t$, $[ns]$',
                          ylabel='$\\rho$, $[kg/m^3]$',
                          fontsize=15, legend_size=legend_size,
                          figsize=(8, 6), dpi=80, loc='lower left',
                          save_name="multi_density_gas.png")

    plot_value_evolution(txt_file='mass_flow_gas_evolution.txt',
                          title='Gas mass flow evolution at different liquid thickness at $T*$ = {} K'.format(temperature_folder_list[0].replace('T','')),
                          xlabel='$t$, $[ns]$',
                          ylabel='$J$, $[kg/m^2 \cdot s]$',
                          fontsize=15, legend_size=legend_size,
                          figsize=(8, 6), dpi=80, loc='lower right',
                          save_name="multi_mass_flow_gas.png")



def get_value_vs_thickness_in_gas(legend_size):
    txt_file = "GAS_vz_dens_MF.txt"
    vz_list, density_list, MF_list = [], [], []
    pressure_list, t_bias_list = [], []
    for _ in range(len(temperatures_folder_list)):
        vz_list.append([])
        density_list.append([])
        MF_list.append([])
        t_bias_list.append([])
        pressure_list.append([])

    # Начало блока считывания данных скорости vz, плотности и потока массы
    for i, t_folder in enumerate(temperatures_folder_list):
        for layer in layer_foler_list:
            if "Linux" in platform.system():
                txt_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/Txt/{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            if "Windows" in platform.system():
                txt_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\Txt\\{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть

            with open(txt_file_dir, 'r') as r:
                lines = r.readlines()
                for n_line in lines:
                    if n_line.startswith('#'):
                        continue
                    line = n_line.split()
                    vz_list[i].append(float(line[0]))
                    density_list[i].append(float(line[1]))
                    MF_list[i].append(float(line[2]))
                    t_bias_list[i].append(float(line[3]))
                    pressure_list[i].append(float(line[4]))
    # Конец блока считывания данных скорости vz, плотности и потока массы

    # Строим зависимости
    plot_value_vs_thickness(value_list=vz_list, fontsize=15, legend_size=legend_size,
                            xlabel= '$H$, $[nm]$',
                            ylabel='$v_z$, $[m/s]$',
                            title='Gas velocity $v_z$ versus liquid thickness $H$',
                            figsize=(8,6), dpi=80, loc='lower left',
                            save_name='gas_v_z_vs_thickness.png')

    plot_value_vs_thickness(value_list=density_list, fontsize=15, legend_size=legend_size,
                            xlabel='$H$, $[nm]$',
                            ylabel='$\\rho$, $[kg/m^3]$',
                            title='Gas density versus liquid thickness $H$',
                            figsize=(8, 6), dpi=80, loc='lower left',
                            save_name='gas_density_vs_thickness.png')

    plot_value_vs_thickness(value_list=MF_list, fontsize=15, legend_size=legend_size,
                            xlabel='$H$, $[nm]$',
                            ylabel='$J$, $[kg/m^2 \cdot s]$',
                            title='Gas mass flow versus liquid thickness $H$',
                            figsize=(8, 6), dpi=80, loc='lower left',
                            save_name='gas_mass_flow_vs_thickness.png')

    plot_value_vs_thickness(value_list=t_bias_list, fontsize=15, legend_size=legend_size,
                            xlabel='$H$, $[nm]$',
                            ylabel='$T$, $[K]$',
                            title='Gas temperature versus liquid thickness $H$',
                            figsize=(8, 6), dpi=80, loc='lower left',
                            save_name='gas_t_bias_vs_thickness.png')

    plot_value_vs_thickness(value_list=pressure_list, fontsize=15, legend_size=legend_size,
                            xlabel='$H$, $[nm]$',
                            ylabel='$P$, $[bar]$',
                            title='Gas pressure versus liquid thickness $H$',
                            figsize=(8, 6), dpi=80, loc='lower left',
                            save_name='gas_pressure_vs_thickness.png')


def plot_value_vs_thickness(value_list, fontsize, legend_size, xlabel, ylabel, loc, figsize, dpi, title, save_name):
    # Строим зависимости от толщины слоя жидкости
    plt.figure(figsize=figsize, dpi=dpi)
    plt.title(title, fontsize=fontsize, color='black')
    plt.grid()
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':')
    plt.xlabel(xlabel, fontsize=fontsize, color='black')
    plt.ylabel(ylabel, fontsize=fontsize, color='black')
    plt.xlim(thickness_list[0], thickness_list[-1])
    for i in range(len(temperatures_folder_list)):
        plt.plot(thickness_list, value_list[i], '-', label='T*={}[K]'.format(temperatures_folder_list[i].replace('T', '')))
    plt.legend(fontsize=legend_size, loc=loc)
    plt.savefig(save_name)


def plot_massflow_new_vs_old():

    old_massflow_data = [741.77, 646.55, 582.06, 544.89, 533.21, 523.7, 523.14]

    txt_file = "GAS_vz_dens_MF.txt"
    vz_list, density_list, MF_list = [], [], []


    # Начало блока считывания данных скорости vz, плотности и потока массы
    for t_folder in temperature_folder_list:
        for layer in layer_foler_list:
            if "Linux" in platform.system():
                txt_file_dir = main_dir + '/{}'.format(t_folder) + '/{}'.format(layer) + '/Py/Txt/{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть
            if "Windows" in platform.system():
                txt_file_dir = main_dir + '\\{}'.format(t_folder) + '\\{}'.format(layer) + '\\Py\\Txt\\{}'.format(
                    txt_file)  # директория txt_file, который нужно открыть

            with open(txt_file_dir, 'r') as r:
                lines = r.readlines()
                for n_line in lines:
                    if n_line.startswith('#'):
                        continue
                    line = n_line.split()
                    vz_list.append(float(line[0]))
                    density_list.append(float(line[1]))
                    MF_list.append(float(line[2]))
    # Конец блока считывания данных скорости vz, плотности и потока массы
    value_list = MF_list
    fontsize = 15
    legend_size = 11
    xlabel = '$H$, $[nm]$'
    ylabel = '$J$, $[kg/m^2 \cdot s]$'
    title = 'Gas mass flow versus liquid thickness $H$'
    figsize = (8, 6)
    dpi = 80
    loc = 'lower left'
    save_name = 'massflow_new_vs_old.png'

    plt.figure(figsize=figsize, dpi=dpi)
    plt.title(title, fontsize=fontsize, color='black')
    plt.grid()
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':')
    plt.xlabel(xlabel, fontsize=fontsize, color='black')
    plt.ylabel(ylabel, fontsize=fontsize, color='black')
    plt.xlim(thickness_list[0], thickness_list[-1])
    plt.plot(thickness_list, MF_list, '-', label='NEW T*=100[K]')
    plt.plot(thickness_list, old_massflow_data, '-', label='Диссертация T*=100[K]')
    plt.legend(fontsize=legend_size, loc=loc)
    plt.savefig(save_name)


def plot_interface_evolution(legend_size):
    plot_value_evolution(txt_file='interface_coord.txt',
                         title='Evolution liquid surface location at $T*$ = {} K'.format(
                             temperature_folder_list[0].replace('T', '')),
                         xlabel='$t$, $[ns]$',
                         ylabel='$z$, $[nm]$',
                         fontsize=15, legend_size=legend_size,
                         figsize=(8, 6), dpi=80, loc='upper right',
                         save_name="interface_coord.png")

    plot_value_evolution(txt_file='interface_density.txt',
                         title='Evolution liquid surface density at $T*$ = {} K'.format(
                             temperature_folder_list[0].replace('T', '')),
                         xlabel='$t$, $[ns]$',
                         ylabel='$\\rho$, $[kg/m^3]$',
                         fontsize=15, legend_size=legend_size,
                         figsize=(8, 6), dpi=80, loc='lower left',
                         save_name="interface_density.png")

    plot_value_evolution(txt_file='interface_temperature.txt',
                         title='Evolution liquid surface temperature at $T*$ = {} K'.format(
                             temperature_folder_list[0].replace('T', '')),
                         xlabel='$t$, $[ns]$',
                         ylabel='$T$, $[K]$',
                         fontsize=15, legend_size=legend_size,
                         figsize=(8, 6), dpi=80, loc='lower left',
                         save_name="interface_temperature.png")

if __name__ == '__main__':
    #run_create_in()  # Обновляем папку Py в каждом каталоге
    #run_data_processing()  # Запускаем обработку данных во всех папках, создавая выходные файлы
    #test_latex()
    #latex_vz_density_MF()  # Создаем LATEX таблицу с vz, плотностью и потоком массы, только после run_data_processing!
    #plot_all_profiles(legend_size=11)  # Строим профили всех макроскопических величин по всему пространству и в газе
    #plot_all_evolutions(legend_size=11)  # Строим эволюцию всех макроскопических величин в газе
    #get_value_vs_thickness_in_gas(legend_size=11)  # Строим зависимость макроскопических величин в газе от толщины слоя
    #plot_massflow_new_vs_old()
    plot_interface_evolution(legend_size=11)



