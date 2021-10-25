import inspect
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from PIL import Image
from tqdm import tqdm
import platform

N_SIMULATIONS = 3
N_VALUES = 14


def add(x,y):
    """ Функция суммирует элементы списка и возвращает список (результат суммы элементов двух списков)"""
    return list(map(lambda a, b: a + b, x, y))


def multiply(x,y):
    """ Функция умножает элементы списка и возвращает список (результат произведения элементов двух списков)"""
    return list(map(lambda a, b: a * b, x, y))


def create_gif():
    # filepaths
    fp_in = "*png"
    fp_out = "image.gif"

    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs,
             save_all=True, duration=250, loop=0)


def os_working():
    try:
        os.mkdir('Img')
    except: pass

    try:
        os.mkdir('Txt')
    except: pass

    print("Current OS is ", platform.system())
    if "Linux" in platform.system():
        main_dir = os.getcwd().replace('/Py', '').replace('Lammps', '/PyLammps')
    if "Windows" in platform.system():
        main_dir = os.getcwd().replace('\\Py', '').replace('Lammps', '\\PyLammps')
        print(main_dir)
    os.chdir(main_dir)
    my_dir = create_path_to_data(main_dir, N_SIMULATIONS)
    data = get_data(my_dir)
    return data


def create_path_to_data(main_dir, N_SIMULATIONS):
    my_dir = []
    for i in range(N_SIMULATIONS):
        my_dir.append(str(i+1))
    # Create path to every work dir
    for i in range(len(my_dir)):
        if "Linux" in platform.system():
            my_dir[i] = main_dir + '/S{}'.format(str(my_dir[i]))
        if "Windows" in platform.system():
            my_dir[i] = main_dir + '\S{}'.format(str(my_dir[i]))
    return my_dir


def make_choose_dir_for_out_data(func_name):
    """Создает папку с названием функции и переходит в нее"""
    if "Linux" in platform.system():
        if r'/Py/Img' not in os.getcwd():
            os.chdir(os.getcwd() + r'/Py/Img')

    if "Windows" in platform.system():
        if r'\Py\Img' not in os.getcwd():
            os.chdir(os.getcwd() + r'\Py\Img')
    try:
        os.makedirs(func_name)
    except:
        pass
    os.chdir(func_name)


def get_data(my_dir):
    """ Create path to every data file"""
    log_path, s2_d_t_vz_path, s2_p_path, s2_t_bias_path, s2_rdf_g_path, s2_rdf_l_path = [], [], [], [], [], []
    s3_d_t_vz_path, s3_p_path, s3_t_bias_path = [], [], []
    s4_d_t_vz_path, s4_p_path, s4_t_bias_path = [], [], []
    data_list = (log_path, s2_d_t_vz_path, s2_p_path, s2_t_bias_path, s2_rdf_g_path, s2_rdf_l_path,
                 s3_d_t_vz_path, s3_p_path, s3_t_bias_path,
                 s4_d_t_vz_path, s4_p_path, s4_t_bias_path)

    for i in range(len(my_dir)):
        for file in os.listdir(my_dir[i]):
            if 'lammps' in file:
                log_path = my_dir[i] + '/{}'.format(file)
                data_list[0].append(log_path)
            if 'S2_Density_T_vz' in file:
                s2_d_t_vz_path = my_dir[i] + '/{}'.format(file)
                data_list[1].append(s2_d_t_vz_path)
            if 'S2_P_prof' in file:
                s2_p_path = my_dir[i] + '/{}'.format(file)
                data_list[2].append(s2_p_path)
            if 'S2_T_bias' in file:
                s2_t_bias_path = my_dir[i] + '/{}'.format(file)
                data_list[3].append(s2_t_bias_path)
            if 'S2_RDF_G' in file:
                s2_rdf_g_path = my_dir[i] + '/{}'.format(file)
                data_list[4].append(s2_rdf_g_path)
            if 'S2_RDF_L' in file:
                s2_rdf_l_path = my_dir[i] + '/{}'.format(file)
                data_list[5].append(s2_rdf_l_path)
            if 'S3_Density_T_vz' in file:
                s3_d_t_vz_path = my_dir[i] + '/{}'.format(file)
                data_list[6].append(s3_d_t_vz_path)
            if 'S3_P_prof' in file:
                s3_p_path = my_dir[i] + '/{}'.format(file)
                data_list[7].append(s3_p_path)
            if 'S3_T_bias' in file:
                s3_t_bias_path = my_dir[i] + '/{}'.format(file)
                data_list[8].append(s3_t_bias_path)
    return data_list


def how_much_averages(arg, length):
    """ Определяем количество усреднений расчета макроскопических величин"""
    with open(arg, 'r') as r:
        counter = 0
        lines = r.readlines()
        for n_line in lines:
            line = n_line.split()
            if len(line) == length:
                counter += 1
    return counter


def save_fig(file_number):
    """ Костыли для корректной сортировки """
    if len(str(file_number)) == 1:
        plt.savefig('000{}.png'.format(str(file_number)))
    if len(str(file_number)) == 2:
        plt.savefig('00{}.png'.format(str(file_number)))
    if len(str(file_number)) == 3:
        plt.savefig('0{}.png'.format(str(file_number)))


def create_main_list(N_simulation, N_values, data):
    """ Создаем многомерный редактируемый массив для симуляций->величин->усреднений->списка значений->чанков"""

    log = data[0]
    s2_d_t_vz_file_list, s2_p_file_list, s2_t_bias_file_list = data[1], data[2], data[3]
    s2_rdf_g_file_list, s2_rdf_l_file_list = data[4], data[5]
    s3_d_t_vz_file_list, s3_p_file_list, s3_t_bias_file_list = data[6], data[7], data[8]

    stage_2 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    stage_3 = [9, 10, 11, 12, 13]

    folders_list = []
    for i in range(N_simulation):
        folders_list.append([])
        for k in range(N_values):
            folders_list[i].append([])
            if k in stage_2:
                N_averages = how_much_averages(s2_d_t_vz_file_list[0], 3)
            if k in stage_3:
                N_averages = how_much_averages(s3_d_t_vz_file_list[0], 3)
            for s in range(N_averages):
                folders_list[i][k].append([])
    #print("Количество симуляций в базе: ", len(folders_list))
    #print("Количество величин в базе: ", len(folders_list[0]))
    #print("Количество усреднений для st2 coord: ", len(folders_list[0][0]))
    return folders_list


def read_data(data):
    log = data[0]
    s2_d_t_vz_file_list, s2_p_file_list, s2_t_bias_file_list = data[1], data[2], data[3]
    s2_rdf_g_file_list, s2_rdf_l_file_list = data[4], data[5]
    s3_d_t_vz_file_list, s3_p_file_list, s3_t_bias_file_list = data[6], data[7], data[8]

    folders_list = create_main_list(N_simulation=len(log), N_values=N_VALUES, data=data)
    number_of_folders = len(folders_list)

    for i in range(number_of_folders):

        coord_list = []  # z-coordinate list [A] Номер элемента [i][s][0]
        s2_bias_t_list = []  # bias temperature profile
        s2_t_list = []  # usual temperature profile
        s2_p_list = []  # press per atom [bar]
        s2_density_list = []  # density list [g/cm3]
        s2_vz_list = []  # vz profile [A/ps]
        s2_rdf_coord_list = []  # [A]
        s2_rdf_g_list = []
        s2_rdf_l_list = []

        s3_bias_t_list = []  # bias temperature profile
        s3_t_list = []  # usual temperature profile
        s3_p_list = []  # press per atom [bar]
        s3_density_list = []  # density list [g/cm3]
        s3_vz_list = []  # vz profile [A/ps]

        with open(s2_d_t_vz_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 3 and check == False:
                    continue
                if len(line) > 3:
                    coord = float(line[-5]) / 10  # [nm]
                    density = float(line[-3]) * 1000  # [kg/m3]
                    temperature = float(line[-2])  # [K]
                    vz = float(line[-1])*100  # [m/s]
                    coord_list.append(coord)
                    s2_density_list.append(density)
                    s2_t_list.append(temperature)
                    s2_vz_list.append(vz)
                    check = True
                if len(line) == 3 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][0][s] = coord_list
                    folders_list[i][1][s] = s2_density_list
                    #if s < 2: print('s1: ', i, s, folders_list[0][1][1])
                    #if s < 2: print('s2: ', i, s, folders_list[1][1][1], '\n')
                    folders_list[i][2][s] = s2_t_list
                    folders_list[i][3][s] = s2_vz_list
                    coord_list, s2_density_list, s2_t_list, s2_vz_list = [], [], [], []
                    s += 1

        with open(s2_p_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 3 and check == False:
                    continue
                if len(line) > 3:
                    pp = float(line[-1])
                    number_of_atoms = float(line[-2])
                    pressure = pp * number_of_atoms
                    s2_p_list.append(pressure)
                    check = True

                if len(line) == 3 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][4][s] = s2_p_list  # Элемент [i][s][4]
                    s2_p_list = []
                    s += 1

        with open(s2_t_bias_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 2 and check == False:
                    continue
                if len(line) > 2:
                    bias_t = float(line[-1])
                    s2_bias_t_list.append(bias_t)
                    check = True

                if len(line) == 2 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][5][s] = s2_bias_t_list  # Элемент [i][s][5]
                    s2_bias_t_list = []
                    s += 1

        with open(s2_rdf_g_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 2 and check == False:
                    continue
                if len(line) > 2:
                    rdf_coord = float(line[-3])
                    rdf_value = float(line[-2])
                    s2_rdf_coord_list.append(rdf_coord)
                    s2_rdf_g_list.append(rdf_value)
                    check = True

                if len(line) == 2 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][6][s] = s2_rdf_coord_list  # Элемент [i][s][6]
                    folders_list[i][7][s] = s2_rdf_g_list  # Элемент [i][s][7]
                    s2_rdf_coord_list, s2_rdf_g_list = [], []
                    s += 1

        with open(s2_rdf_l_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 2 and check == False:
                    continue
                if len(line) > 2:
                    rdf_value = float(line[-2])
                    s2_rdf_l_list.append(rdf_value)
                    check = True
                if len(line) == 2 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][8][s] = s2_rdf_l_list  # Элемент [i][s][8]
                    s2_rdf_l_list = []
                    s += 1

        with open(s3_d_t_vz_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 3 and check == False:
                    continue
                if len(line) > 3:
                    coord = float(line[-5]) / 10  # [nm]
                    density = float(line[-3]) * 1000  # [kg/m3]
                    temperature = float(line[-2])  # [K]
                    vz = float(line[-1])*100  # [m/s]
                    coord_list.append(coord)
                    s3_density_list.append(density)
                    s3_t_list.append(temperature)
                    s3_vz_list.append(vz)
                    check = True
                if len(line) == 3 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][9][s] = s3_density_list  # Элемент [i][s][9]
                    folders_list[i][10][s] = s3_t_list  # Элемент [i][s][10]
                    folders_list[i][11][s] = s3_vz_list  # Элемент [i][s][11]
                    coord_list, s3_density_list, s3_t_list, s3_vz_list = [], [], [], []
                    s += 1

        with open(s3_p_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 3 and check == False:
                    continue
                if len(line) > 3:
                    pp = float(line[-1])
                    number_of_atoms = float(line[-2])
                    pressure = pp * number_of_atoms
                    s3_p_list.append(pressure)
                    check = True
                if len(line) == 3 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][12][s] = s3_p_list  # Элемент [i][s][12]
                    s3_p_list = []
                    s += 1

        with open(s3_t_bias_file_list[i], 'r') as r:
            s = 0
            check = False
            lines = r.readlines()
            for n_line in lines:
                if n_line.startswith('#'):
                    continue
                line = n_line.split()
                if len(line) == 2 and check == False:
                    continue
                if len(line) > 2:
                    bias_t = float(line[-1])
                    s3_bias_t_list.append(bias_t)
                    check = True
                if len(line) == 2 and check:
                    """В момент s (ex. 20_000) имеем список со списками(в которых профили величин)"""
                    folders_list[i][13][s] = s3_bias_t_list  # Элемент [i][s][13]
                    s3_bias_t_list = []
                    s += 1

    # TODO Доделать эволюцию полной энергии и температуру системы
    """ ЭВОЛЮЦИЯ ПОЛНОЙ ЭНЕРГИИ И ТЕМПЕРАТУРЫ ОТДЕЛЬНО"""

    return folders_list


def delete_points(value, N_left_side, N_right_side):
    """This func del first and last point with zero number of particles, temperature and so on"""
    if N_left_side != 0 or N_right_side != 0:
        for i in range(N_left_side):
            del value[0]
        for i in range(N_right_side):
            del value[-1]
    else: pass


def average_by_simulation(results, value_number, N_SIMULATIONS):
    """Функция усреднения величины по симуляциям:
    Вернет массив results с усредненными значениями в первую симуляцию!
    HOW TO USE: EXAMPLE
    results = average_by_simulation(results, value_number, N_SIMULATIONS)"""
    k = value_number
    N_AVERAGES = len(results[0][k])  # Количество усреднений величины под номером k
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    for i in range(1, N_SIMULATIONS):
        for s in range(N_AVERAGES-1):
            for m in range(N_CHUNKS):
                results[0][k][s][m] += results[i][k][s][m]  # суммируем температуру в первую симуляцию
            if i == N_SIMULATIONS - 1:  # Если находимя на последней симуляции, то еще и делим на их количество = mean
                for m in range(N_CHUNKS):
                    results[0][k][s][m] = results[0][k][s][m] / N_SIMULATIONS  # усредняем температуру по симуляциям
    return results


def plot_temperature_bias(results):
    number_particles_list = results[0]
    bias_temperature_list = results[1]
    temperature_list = results[2]
    coord_list = results[3]
    density_list = results[4]

    plt.subplot(1, 1, 1)
    plt.grid()
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':')
    plt.title('Профиль температуры при разном количестве частиц', color='black', fontsize=12)
    plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
    plt.ylabel('Температура с учетом гидродинамической скорости, [K]', fontsize=16, color='blue')
    plt.xlim([0, 120])
    for i, name in enumerate(number_particles_list):
        plt.plot(coord_list[i], bias_temperature_list[i], '-', label='{}'.format(name))
    plt.legend()
    plt.show()


def test_lists(folders_list):
    i = 0  # Номер симуляции
    k = 0  # Номер величины
    s = 0  # Номер усреднения
    m = 0  # Номер чанка в профиле
    print("Количество папок: ", len(folders_list))
    print('Количество выводимых величн в {} папке:'.format(i), len(folders_list[i]))
    print('Количество усреднений в {} папке в {} величине: '.format(i,k), len(folders_list[i][k]))
    print('Количество чанков в усреднении {}:'.format(s), len(folders_list[i][k][s]))

    print('>>Пример 1: вывод двух последующих усредненных плотностей для первой папки:')
    # То есть для указания величины меняем 2 столбик, для момента времени 3
    density_list_from_f1_ave1 = folders_list[0][1][0]
    density_list_from_f1_ave2 = folders_list[0][1][1]
    print(density_list_from_f1_ave1, '\n', density_list_from_f1_ave2)

    print('>>Пример 2: вывод плотности из двух разных симуляций на первом временном шаге:')
    density_list_from_f1_ave1 = folders_list[0][1][0]
    density_list_from_f2_ave1 = folders_list[1][1][0]
    print(density_list_from_f1_ave1, '\n', density_list_from_f2_ave1)


def plot_t_bias_st2(results):
    """Эволюция профиля температуры bias STAGE 2 only"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)
    coord_list = results[0][0]
    t_list = results[0][5]
    xmax = coord_list[0][-1]
    for s in range(len(coord_list)-1):
        dt = int((s+1) * 20000*0.005)
        file_number = s + 1
        mean_t = np.mean(t_list[s])
        min_max_t_list = (abs(mean_t - min(t_list[s])), abs(mean_t - max(t_list[s])))
        #print(min_max_t_list)
        delta_t = round(max(min_max_t_list), 2)

        plt.subplot(1, 1, 1)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.title('Профиль температуры на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list[s], t_list[s], '-')
        plt.text(99, 108, '$\Delta T$ = {} [K]'.format(delta_t), fontsize=15, color='green')

        save_fig(file_number)
        plt.close()
    create_gif()


def plot_t_bias_dens_st2(results):
    """Эволюция профиля T_bias + density STAGE 2 only [EQUILIBRATION]"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)
    coord_list = results[0][0]
    t_list = results[0][5]
    d_list = results[0][1]
    xmax = coord_list[0][-1]

    for s in range(len(coord_list) - 1):
        dt = int((s + 1) * 20000 * 0.005)
        file_number = s + 1
        mean_t = np.mean(t_list[s])
        min_max_t_list = (abs(mean_t - min(t_list[s])), abs(mean_t - max(t_list[s])))
        # print(min_max_t_list)
        delta_t = round(max(min_max_t_list), 2)


        plt.figure(figsize=(14,6))

        plt.subplot(1, 2, 1)
        plt.suptitle('Профиль температуры и плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black',
                     fontsize=12)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list[s], t_list[s], '-')
        plt.text(99, 108, '$\Delta T$ = {} [K]'.format(delta_t), fontsize=15, color='green')

        plt.subplot(1, 2, 2)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        #plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        #plt.title('Профиль плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[s], d_list[s], '-', color='red')

        save_fig(file_number)
        plt.close()
    create_gif()


def plot_t_bias_dens_st2_st3(results):  # TODO
    """Эволюция профиля T_bias + density STAGE 2-3-4"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]
    xmax = coord_list[0][-1]
    t_list_st2 = results[0][5]
    d_list_st2 = results[0][1]
    t_list_st3 = results[0][13]
    d_list_st3 = results[0][9]
    t_list_st4 = results[0][18]
    d_list_st4 = results[0][14]

    print('Начало обработки [STAGE 2]')
    for s in tqdm(range(len(t_list_st2) - 1)):
        dt = int((s + 1) * 20000 * 0.005)
        file_number = s + 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle('[STAGE 2] - EQUILIBRATION Профиль температуры и плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black',
                     fontsize=12)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list[s], t_list_st2[s], '-')

        plt.subplot(1, 2, 2)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        # plt.title('Профиль плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[s], d_list_st2[s], '-', color='red')

        save_fig(file_number)
        plt.close()

    # STAGE 3:
    print('Начало обработки [STAGE 3]')
    for s in tqdm(range(len(t_list_st3) - 1)):
        dt = int((s + 1 + len(t_list_st2) - 1) * 20000 * 0.005)
        file_number = s + 1 + len(t_list_st2) - 1
        plt.figure(figsize=(14, 6))

        # Подгоняем количество профилей координат чтобы количество списков координат было равно количеству списков температур:
        coord_list_st3 = coord_list
        """for _ in range(len(coord_list)-len(t_list_st3)):
            del (coord_list_st3[-1])"""

        plt.subplot(1, 2, 1)
        plt.suptitle('[STAGE 3] STABILIZATION Профиль температуры и плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black',
                     fontsize=12)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(40, 115)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list_st3[s], t_list_st3[s], '-')

        plt.subplot(1, 2, 2)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list_st3[s], d_list_st3[s], '-', color='red')

        save_fig(file_number)
        plt.close()

    create_gif()


def plot_AVE_t_bias_dens_st2_st3(results, N_SIMULATIONS):
    """Усрдненная по симуляциям эволюция профиля T_bias + density STAGE 2-3"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]  # список с профилями в разные моменты времени
    xmax = coord_list[0][-1]

    N_AVERAGES_st2 = len(results[0][5])  # Количество усреднений по времени в STAGE 2
    N_AVERAGES_st3 = len(results[0][13])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    all_t_list_st2 = results[0][5][0]
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''
    # Усреднение температуры и плотности по симуляциям [STAGE 2]
    results = average_by_simulation(results, 5, N_SIMULATIONS)  # Усреднение температуры по симуляциям
    results = average_by_simulation(results, 1, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    # Усреднение температуры и плотности по симуляциям [STAGE 3]
    results = average_by_simulation(results, 13, N_SIMULATIONS)  # Усреднение температуры по симуляциям
    results = average_by_simulation(results, 9, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    t_list_st2 = results[0][5]
    d_list_st2 = results[0][1]
    t_list_st3 = results[0][13]
    d_list_st3 = results[0][9]

    print('Начало обработки [STAGE 2]')
    delta_density = 0
    old_density = 0
    for s in tqdm(range(len(t_list_st2) - 1)):
        dt = int((s + 1) * 20000 * 0.005)/1000  # [ns]
        file_number = s + 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)

        plt.suptitle(
            '[STAGE 2] - EQUILIBRATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list[s], t_list_st2[s], '-')

        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st2[s]), 2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        # plt.title('Профиль плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[0], d_list_st2[s], '-', color='red')

        save_fig(file_number)
        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()

    # STAGE 3:
    print('Начало обработки [STAGE 3]')
    for s in tqdm(range(len(t_list_st3) - 1)):
        dt = int((s + 1 + len(t_list_st2) - 1) * 20000 * 0.005)/1000  # [ns]
        file_number = s + 1 + len(t_list_st2) - 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle(
            '[STAGE 3] - EVAPORATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        plt.ylim(40, 115)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Температура, [K]', fontsize=12, color='blue')
        plt.plot(coord_list[0], t_list_st3[s], '-')


        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st3[s]),2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(0, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[0], d_list_st3[s], '-', color='red')

        save_fig(file_number)
        
        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()
    create_gif()


def plot_AVE_pressure_dens_st2_st3(results, N_SIMULATIONS, N_left_side, N_right_side):
    """Усрдненная по симуляциям эволюция профиля Pressure + density STAGE 2-3"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]  # список с профилями в разные моменты времени


    N_AVERAGES_st2 = len(results[0][4])  # Количество усреднений по времени в STAGE 2
    N_AVERAGES_st3 = len(results[0][12])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''
    # Усреднение температуры и плотности по симуляциям [STAGE 2]
    results = average_by_simulation(results, 4, N_SIMULATIONS)  # Усреднение температуры по симуляциям
    results = average_by_simulation(results, 1, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    # Усреднение температуры и плотности по симуляциям [STAGE 3]
    results = average_by_simulation(results, 12, N_SIMULATIONS)  # Усреднение температуры по симуляциям
    results = average_by_simulation(results, 9, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    p_list_st2 = results[0][4]
    d_list_st2 = results[0][1]
    p_list_st3 = results[0][12]
    d_list_st3 = results[0][9]

    delete_points(coord_list[0], N_left_side, N_right_side)  # Убираем точки слева и справа !!!!
    xmax = coord_list[0][-1]
    xmin = coord_list[0][0]

    print('Начало обработки [STAGE 2]')
    delta_density = 0
    old_density = 0
    for s in tqdm(range(len(p_list_st2) - 1)):
        dt = int((s + 1) * 20000 * 0.005) / 1000  # [ns]
        file_number = s + 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)

        plt.suptitle(
            '[STAGE 2] - EQUILIBRATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        #plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Давление, [бар]', fontsize=12, color='blue')

        delete_points(p_list_st2[s], N_left_side, N_right_side)
        plt.plot(coord_list[0], p_list_st2[s], '-')

        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st2[s]), 2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        # plt.title('Профиль плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')

        delete_points(d_list_st2[s], N_left_side, N_right_side)
        plt.plot(coord_list[0], d_list_st2[s], '-', color='red')

        save_fig(file_number)
        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()

    # STAGE 3:
    print('Начало обработки [STAGE 3]')
    for s in tqdm(range(len(p_list_st3) - 1)):
        dt = int((s + 1 + len(p_list_st2) - 1) * 20000 * 0.005) / 1000  # [ns]
        file_number = s + 1 + len(p_list_st2) - 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle(
            '[STAGE 3] - EVAPORATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        #plt.ylim(40, 115)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Давление, [бар]', fontsize=12, color='blue')

        delete_points(p_list_st3[s], N_left_side, N_right_side)
        plt.plot(coord_list[0], p_list_st3[s], '-')

        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st3[s]), 2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')

        delete_points(d_list_st3[s], N_left_side, N_right_side)
        plt.plot(coord_list[0], d_list_st3[s], '-', color='red')

        save_fig(file_number)

        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()
    create_gif()


def plot_AVE_massflow_dens_st2_st3(results, N_SIMULATIONS, N_left_side, N_right_side):
    """Усрдненная по симуляциям эволюция профиля MASSFLOW + density STAGE 2-3"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]  # список с профилями в разные моменты времени


    N_AVERAGES_st2 = len(results[0][3])  # Количество усреднений по времени в STAGE 2
    N_AVERAGES_st3 = len(results[0][11])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''
    # Усреднение температуры и плотности по симуляциям [STAGE 2]
    results = average_by_simulation(results, 3, N_SIMULATIONS)  # Усреднение vz по симуляциям
    results = average_by_simulation(results, 1, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    # Усреднение температуры и плотности по симуляциям [STAGE 3]
    results = average_by_simulation(results, 11, N_SIMULATIONS)  # Усреднение vz по симуляциям
    results = average_by_simulation(results, 9, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    vz_list_st2 = results[0][3]
    d_list_st2 = results[0][1]
    vz_list_st3 = results[0][11]
    d_list_st3 = results[0][9]

    delete_points(coord_list[0], N_left_side, N_right_side)
    xmax = coord_list[0][-1]
    xmin = coord_list[0][0]

    print('Начало обработки [STAGE 2]')
    delta_density = 0
    old_density = 0
    for s in tqdm(range(len(vz_list_st2) - 1)):
        dt = int((s + 1) * 20000 * 0.005) / 1000  # [ns]
        file_number = s + 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle(
            '[STAGE 2] - EQUILIBRATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        #plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel(r'Поток массы, [$kg/s*m^3$]', fontsize=12, color='blue')
        delete_points(vz_list_st2[s], N_left_side, N_right_side)
        delete_points(d_list_st2[s], N_left_side, N_right_side)
        mass_flow_list = np.array(vz_list_st2[s])*np.array(d_list_st2[s])
        plt.plot(coord_list[0], mass_flow_list, '-')

        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st2[s]), 2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        # plt.title('Профиль плотности на временнном шаге dt = {} [ps]'.format(str(dt)), color='black', fontsize=12)
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[0], d_list_st2[s], '-', color='red')

        save_fig(file_number)
        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()

    # STAGE 3:
    print('Начало обработки [STAGE 3]')
    for s in tqdm(range(len(vz_list_st3) - 1)):
        dt = int((s + 1 + len(vz_list_st2) - 1) * 20000 * 0.005) / 1000  # [ns]
        file_number = s + 1 + len(vz_list_st2) - 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle(
            '[STAGE 3] - EVAPORATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        #plt.ylim(40, 115)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel(r'Поток массы, [$kg/s*m^3$]', fontsize=12, color='blue')
        delete_points(vz_list_st3[s], N_left_side, N_right_side)
        delete_points(d_list_st3[s], N_left_side, N_right_side)
        mass_flow_list = np.array(vz_list_st3[s]) * np.array(d_list_st3[s])
        plt.plot(coord_list[0], mass_flow_list, '-')

        plt.subplot(1, 2, 2)
        max_density = round(max(d_list_st3[s]), 2)
        plt.text(50, 1200, r'$\rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(max_density), fontsize=18, color='red')
        plt.text(50, 1100, r'$\Delta \rho_{MAX}$' + ' = {} [$kg/m^3$]'.format(delta_density), fontsize=18, color='red')
        plt.grid()
        plt.minorticks_on()
        plt.xlim(xmin, xmax)
        # plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [нм]', fontsize=12, color='blue')
        plt.ylabel('Плотность, [$kg/m^3$]', fontsize=12, color='blue')
        plt.plot(coord_list[0], d_list_st3[s], '-', color='red')

        save_fig(file_number)

        delta_density = round((max_density - old_density), 2)
        old_density = max_density

        plt.close()
    create_gif()


def plot_AVE_massflow_density_vz_time_in_gas(results, N_SIMULATIONS, N_left_side, N_right_side):
    """Усрдненная по симуляциям эволюция потока массы, плотности, скорости vz во всей области газа
    Суммируем значения потока массы начиная с N_left_side и заканчивая N_right_side
    делим сумму на количество чанков в области газа"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]  # список с профилями в разные моменты времени

    N_AVERAGES_st2 = len(results[0][3])  # Количество усреднений по времени в STAGE 2
    N_AVERAGES_st3 = len(results[0][11])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''
    # Усреднение vz и плотности по симуляциям [STAGE 2]
    results = average_by_simulation(results, 3, N_SIMULATIONS)  # Усреднение vz по симуляциям
    results = average_by_simulation(results, 1, N_SIMULATIONS)  # Усреднение плотности по симуляциям

    # Усреднение vz и плотности по симуляциям [STAGE 3]
    results = average_by_simulation(results, 11, N_SIMULATIONS)  # Усреднение vz по симуляциям
    results = average_by_simulation(results, 9, N_SIMULATIONS)  # Усреднение плотности по симуляциям
    results = average_by_simulation(results, 12, N_SIMULATIONS)  # Усреднение давления по симуляциям
    results = average_by_simulation(results, 13, N_SIMULATIONS)  # Усреднение температуры bias по симуляциям

    vz_list_st2 = results[0][3]
    d_list_st2 = results[0][1]
    vz_list_st3 = results[0][11]
    d_list_st3 = results[0][9]
    p_list_st3 = results[0][12]
    t_bias_list_st3 = results[0][13]

    massflow_list = []
    time_step_list = []


    for s in range(N_AVERAGES_st2-1):
        massflow = 0
        for m in range(N_CHUNKS):
            if m >= N_left_side and m <= (N_CHUNKS - N_right_side):
                massflow += vz_list_st2[s][m] * d_list_st2[s][m]
        ave_massflow = massflow / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение потока массы в газе
        massflow_list.append(ave_massflow)  # kg/m3*s
        time_step_list.append(int((s + 1) * 20000 * 0.005) / 1000)  # [ns]
    plt.title('[STAGE 2] - EQUILIBRATION: Эволюция потока массы в газе',
            color='black',
            fontsize=14)
    plt.grid()
    plt.minorticks_on()
    #plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('время, [нс]', fontsize=12, color='blue')
    plt.ylabel(r'Поток массы, [$kg/s*m^3$]', fontsize=12, color='blue')
    plt.plot(time_step_list, massflow_list, '-')
    plt.savefig('MASSFLOW_GAS_TIME_STAGE2.png')
    plt.close()

    massflow_list = []
    ave_density_list = []
    ave_vz_list = []
    time_step_list = []
    ave_pressure_list = []
    ave_t_bias_list = []

    for s in range(N_AVERAGES_st3-1):
        massflow = 0
        current_density = 0
        current_vz = 0
        current_press = 0
        current_t_bias = 0
        for m in range(N_CHUNKS):
            if m >= N_left_side and m <= (N_CHUNKS - N_right_side):
                massflow += vz_list_st3[s][m] * d_list_st3[s][m]
                current_density += d_list_st3[s][m]
                current_vz += vz_list_st3[s][m]
                current_t_bias += t_bias_list_st3[s][m]
                current_press += p_list_st3[s][m]
        ave_massflow = massflow / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение потока массы в газе
        ave_density = current_density / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение плотности в газе
        ave_vz = current_vz / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение потока массы в газе
        ave_t_bias = current_t_bias / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение потока массы в газе
        ave_press = current_press / (N_CHUNKS - N_left_side - N_right_side)  # среднее значение потока массы в газе
        massflow_list.append(ave_massflow)  # kg/m2*s
        ave_density_list.append(ave_density)  # kg/m3
        ave_vz_list.append(ave_vz)  # m/s
        ave_pressure_list.append(ave_press)  # bar
        ave_t_bias_list.append(ave_t_bias)  # K

        time_step_list.append(int((s + 1 + len(vz_list_st2) - 1) * 20000 * 0.005) / 1000)  # [ns]
    plt.title('[STAGE 3] - EVAPORATION: Эволюция потока массы в газе',
              color='black',
              fontsize=14)
    plt.grid()
    plt.minorticks_on()
    # plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('время, [нс]', fontsize=12, color='blue')
    plt.ylabel(r'Поток массы, [$kg/s*m^3$]', fontsize=12, color='blue')
    plt.plot(time_step_list, massflow_list, '-')
    plt.savefig('MASSFLOW_GAS_TIME_STAGE3.png')
    plt.close()

    # save txt
    file_name = 'mass_flow_gas_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      MASSFLOW [kg/m2s]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i],massflow_list[i]))

    # save txt
    file_name = 'density_gas_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      density [kg/m3]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], ave_density_list[i]))

    # save txt
    file_name = 'vz_gas_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      vz [m/s]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], ave_vz_list[i]))

    # save txt
    file_name = 'press_gas_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      Pressure [bar]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], ave_pressure_list[i]))

    # save txt
    file_name = 't_bias_gas_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      T_bias [K]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], ave_t_bias_list[i]))


def AVE_profiles_by_time(results, N_SIMULATIONS):
    """
    Усредняем профили по времени в STAGE3 после 16 нс, строим графики .png
    Для этого:
    0) Усредняем по симуляциям
    1) Определяем усреднение S , которое соответствует t = 16 нс
    2) Определяем оставшееся количество усреднений, по их кол-ву будем усреднять
    3) В усреднение S суммируем все последующие усреднения
    4) В конце расчета для величины K производим усреднение по количеству используемых усреднений
    5) Строим график и переходим к следующей величине

    Здесь для [STAGE 3] плотность - s=9, температура с учетом гидродинамической скорости - s=13,
    скорость vz - s=11, давление - s=12,  координата - s=0
    """
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    k_list = [9, 13, 11, 12]
    for k in k_list:
        results = average_by_simulation(results, k, N_SIMULATIONS)  # Усреднение величин по симуляциям

    coord_list = results[0][0][0]
    N_AVERAGES_st3 = len(results[0][11])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    """ Старт STAGE 3 в момент t = 10 нс. Каждое усреднение = 20_000 шагов = 0.1 нс =>
    => начать усреднения должны с 60-го усреднения S"""
    s_start_ave = 60
    N_ave_steps = N_AVERAGES_st3 - 1 - s_start_ave  # Количество шагов для усреднения
    for k in k_list:
        for s in range(N_AVERAGES_st3-1):
            if s <= 60:  # Если не достигли нужного усреднения, то скипаем
                continue
            results[0][k][s_start_ave] = add(results[0][k][s_start_ave], results[0][k][s])  # Суммируем профили
        results[0][k][s_start_ave] = [m / N_ave_steps for m in results[0][k][s_start_ave]]  # Усредняем их

    density_profile = results[0][9][s_start_ave]
    temperature_bias_profile = results[0][13][s_start_ave]
    vz_profile = results[0][11][s_start_ave]
    pressure_profile = results[0][12][s_start_ave]
    massflow_profile = multiply(density_profile, vz_profile)

    file_name = 'profile_temperature_bias.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name),
                                           '\\Txt\\') + file_name
    with open(txt_file_dir, 'w') as w:
        w.write('# coord [nm]      temerature_bias [K]\n')
        for i in range(len(coord_list)):
            w.write('{}   {}\n'.format(coord_list[i], temperature_bias_profile[i]))

    file_name = 'profile_density.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name),
                                           '\\Txt\\') + file_name
    with open(txt_file_dir, 'w') as w:
        w.write('# coord [nm]      density [kg/m3]\n')
        for i in range(len(coord_list)):
            w.write('{}   {}\n'.format(coord_list[i], density_profile[i]))

    file_name = 'profile_massflow.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name),
                                           '\\Txt\\') + file_name
    with open(txt_file_dir, 'w') as w:
        w.write('# coord [nm]      massflow [kg/m2s]\n')
        for i in range(len(coord_list)):
            w.write('{}   {}\n'.format(coord_list[i], massflow_profile[i]))

    file_name = 'profile_pressure.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name),
                                           '\\Txt\\') + file_name
    with open(txt_file_dir, 'w') as w:
        w.write('# coord [nm]      pressure [bar]\n')
        for i in range(len(coord_list)):
            w.write('{}   {}\n'.format(coord_list[i], pressure_profile[i]))

    file_name = 'profile_vz.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name),
                                           '\\Txt\\') + file_name
    with open(txt_file_dir, 'w') as w:
        w.write('# coord [nm]      vz [m/s]\n')
        for i in range(len(coord_list)):
            w.write('{}   {}\n'.format(coord_list[i], vz_profile[i]))

    delete_points(density_profile, 2, 5)
    delete_points(temperature_bias_profile, 2, 5)
    delete_points(pressure_profile, 2, 5)
    delete_points(vz_profile, 2, 5)
    delete_points(coord_list, 2, 5)
    delete_points(massflow_profile, 2, 5)



    xmin = coord_list[0]
    xmax = coord_list[-1]
    # На данном этапе можно выводить численные данные или визуализировать

    """Профиль температуры и плотности"""
    plt.figure(figsize=(14, 6))
    plt.subplot(1,2,1)
    plt.suptitle('[STAGE 3] - EVAPORATION: Усредненные данные по 6 нс',
              color='black',
              fontsize=14)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Температура, [K]', fontsize=12, color='blue')
    plt.plot(coord_list, temperature_bias_profile, '-')

    plt.subplot(1, 2, 2)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Плотность, [$kg/m^3$]', fontsize=12, color='blue')
    plt.plot(coord_list, density_profile, '-', color = 'red')
    plt.savefig('TEMP_Dens_PROFILE_ave_6ns_STAGE3.png')
    plt.close()

    """Профиль давления и плотности"""
    plt.figure(figsize=(14, 6))
    plt.subplot(1,2,1)
    plt.suptitle('[STAGE 3] - EVAPORATION: Усредненные данные по 6 нс',
              color='black',
              fontsize=14)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Давление, [бар]', fontsize=12, color='blue')
    plt.plot(coord_list, pressure_profile, '-')

    plt.subplot(1, 2, 2)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(xmin, xmax)
    # plt.ylim(40, 115)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Плотность, [$kg/m^3$]', fontsize=12, color='blue')
    plt.plot(coord_list, density_profile, '-', color = 'red')
    plt.savefig('PRESS_Dens_PROFILE_ave_6ns_STAGE3.png')
    plt.close()

    """Профиль потока массы и плотности в газе"""
    plt.figure(figsize=(14, 6))
    plt.subplot(1,2,1)
    plt.suptitle('[STAGE 3] - EVAPORATION: Усредненные данные по 6 нс в ГАЗЕ',
              color='black',
              fontsize=14)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(45, xmax)
    plt.ylim(400, 450)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Поток массы в газе, [$kg/s m^2$]', fontsize=12, color='blue')
    plt.plot(coord_list, massflow_profile, '-')

    plt.subplot(1, 2, 2)
    plt.grid()
    plt.minorticks_on()
    plt.xlim(45, xmax)
    plt.ylim(0, 5)
    plt.grid(which='minor', linestyle=':')
    plt.xlabel('Координата, [нм]', fontsize=12, color='blue')
    plt.ylabel(r'Плотность, [$kg/m^3$]', fontsize=12, color='blue')
    plt.plot(coord_list, density_profile, '-', color = 'red')
    plt.savefig('GAS_MASSFLOW_Dens_PROFILE_ave_6ns_STAGE3.png')
    plt.close()


def plot_AVE_RDF_L_G_st2(results, N_SIMULATIONS):
    """Усредненная по симуляциям эволюция радиальной функции распределения RDF в жидкости STAGE 2"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = [0.0544, 0.1632, 0.272, 0.3808, 0.4896, 0.5984, 0.7072, 0.816, 0.9248, 1.0336, 1.1424, 1.2512,
                  1.36, 1.4688, 1.5776, 1.6864, 1.7952, 1.904, 2.0128, 2.1216, 2.2304, 2.3392, 2.448, 2.5568, 2.6656,
                  2.7744, 2.8832, 2.992, 3.1008, 3.2096, 3.3184, 3.4272, 3.536, 3.6448, 3.7536, 3.8624, 3.9712, 4.08,
                  4.1888, 4.2976, 4.4064, 4.5152, 4.624, 4.7328, 4.8416, 4.9504, 5.0592, 5.168, 5.2768, 5.3856, 5.4944,
                  5.6032, 5.712, 5.8208, 5.9296, 6.0384, 6.1472, 6.256, 6.3648, 6.4736, 6.5824, 6.6912, 6.8, 6.9088,
                  7.0176, 7.1264, 7.2352, 7.344, 7.4528, 7.5616, 7.6704, 7.7792, 7.888, 7.9968, 8.1056, 8.2144, 8.3232,
                  8.432, 8.5408, 8.6496, 8.7584, 8.8672, 8.976, 9.0848, 9.1936, 9.3024, 9.4112, 9.52, 9.6288, 9.7376,
                  9.8464, 9.9552, 10.064, 10.1728, 10.2816, 10.3904, 10.4992, 10.608, 10.7168, 10.8256]
    # список координат для RDF_L and RDF_G

    N_AVERAGES_st2 = len(results[0][8])  # Количество усреднений по времени в STAGE 2
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''
    # Усреднение RDF_L RDF_G по симуляциям [STAGE 2]
    results = average_by_simulation(results, 8, N_SIMULATIONS)  # Усреднение RDF_L по симуляциям
    results = average_by_simulation(results, 7, N_SIMULATIONS)  # Усреднение RDF_G по симуляциям

    RDF_L_list_st2 = results[0][8]
    RDF_G_list_st2 = results[0][7]

    print('Начало обработки [STAGE 2]')
    delta_density = 0
    old_density = 0
    for s in tqdm(range(len(RDF_L_list_st2) - 1)):
        dt = int((s + 1) * 20000 * 0.005) / 1000  # [ns]
        file_number = s + 1
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.suptitle(
            '[STAGE 2] - EQUILIBRATION dt = {} [нс]'.format(str(dt)),
            color='black',
            fontsize=14)
        plt.grid()
        plt.minorticks_on()
        #plt.xlim(xmin, xmax)
        #plt.ylim(100, 110)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [А]', fontsize=12, color='blue')
        plt.ylabel(r'RDF LIQUID', fontsize=12, color='blue')
        plt.plot(coord_list, RDF_L_list_st2[s], '-')

        plt.subplot(1, 2, 2)
        plt.grid()
        plt.minorticks_on()
        #plt.xlim(xmin, xmax)
        plt.grid(which='minor', linestyle=':')
        plt.xlabel('Расстояние, [A]', fontsize=12, color='blue')
        plt.ylabel('RDF GAS', fontsize=12, color='blue')
        plt.plot(coord_list, RDF_G_list_st2[s], '-', color='red')
        save_fig(file_number)

        plt.close()
    create_gif()


def AVE_values_in_gas_st3(results, N_SIMULATIONS):
    """Данная функция определяет усредненные по симуляциям, чанкам и ВРЕМЕНИ значения скорости vz, плотности,
     потока массы, температуры и давления в газе в процессе испарения.
    РЕЗУЛЬТАТ РАБОТЫ ФУНКЦИИ: текстовый файл с данными"""
    os.chdir("Py")
    try:
        os.mkdir('Txt')
    except: pass
    os.chdir('Txt')
        
    data_file = 'GAS_vz_dens_MF.txt'
    HEAD = '# vz, [m/s]   density, [kg/m3]   MASS FLOW, [kg/m2*s]   T_bias, [K]    Pressure, [bar] \n'

    start_chunk = 50  # 30 -- межфазная граница для случая с толщиной 40нм
    end_chunk = 95  # 97-98 чанков -- начало зоны удаления частиц
    delta_chunk = end_chunk - start_chunk

    k_list = [9, 13, 11, 12]
    for k in k_list:
        results = average_by_simulation(results, k, N_SIMULATIONS)  # Усреднение величин по симуляциям

    coord_list = results[0][0][0]
    N_AVERAGES_st3 = len(results[0][11])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    """ Старт STAGE 3 в момент t = 10 нс. Каждое усреднение = 20_000 шагов = 0.1 нс =>
    => начать усреднения должны с 60-го усреднения S"""
    s_start_ave = 60
    N_ave_steps = N_AVERAGES_st3 - 1 - s_start_ave  # Количество шагов для усреднения
    for k in k_list:
        for s in range(N_AVERAGES_st3 - 1):
            if s <= 60:  # Если не достигли нужного усреднения, то скипаем
                continue
            results[0][k][s_start_ave] = add(results[0][k][s_start_ave], results[0][k][s])  # Суммируем профили
        results[0][k][s_start_ave] = [m / N_ave_steps for m in results[0][k][s_start_ave]]  # Усредняем их

    density_profile = results[0][9][s_start_ave]
    temperature_bias_profile = results[0][13][s_start_ave]
    vz_profile = results[0][11][s_start_ave]
    pressure_profile = results[0][12][s_start_ave]

    vz_gas, density_gas, mass_flow_gas, temperature_bias_gas, pressure_gas = 0, 0, 0, 0, 0
    for i in range(start_chunk, end_chunk):
        vz_gas += vz_profile[i]
        density_gas += density_profile[i]
        temperature_bias_gas += temperature_bias_profile[i]
        pressure_gas += pressure_profile[i]

    ROUND_ORDER = 2
    vz_gas = round((vz_gas/delta_chunk), ROUND_ORDER)
    density_gas = round((density_gas/delta_chunk), ROUND_ORDER)
    mass_flow_gas = round((vz_gas*density_gas), ROUND_ORDER)
    temperature_bias_gas = round((temperature_bias_gas/delta_chunk), ROUND_ORDER)
    pressure_gas = round((pressure_gas / delta_chunk), ROUND_ORDER)

    with open(data_file, 'w') as w:
        w.write(HEAD)
        w.write('{}   {}   {}   {}   {}'.format(vz_gas, density_gas, mass_flow_gas, temperature_bias_gas, pressure_gas))


def find_interface(results, N_SIMULATIONS, N_left_side, N_right_side, delta_density):
    """Усрдненная по симуляциям эволюция положения поверхности жидкости, ее плотности и температуры
    Суммируем значения потока массы начиная с N_left_side и заканчивая N_right_side
    делим сумму на количество чанков в области газа"""
    make_choose_dir_for_out_data(func_name=inspect.currentframe().f_code.co_name)

    coord_list = results[0][0]  # список с профилями в разные моменты времени

    N_AVERAGES_st3 = len(results[0][11])  # Количество усреднений по времени в STAGE 3
    N_CHUNKS = len(results[0][0][0])  # Количество чанков координат для всех одинаково
    ''' [i] - симуляци [5] - температура [s] - номер усреднения [m] номер чанка 
        Все симуляции будем складывать в первую и потом каждый элемент поделим на количество симуляций 
        для каждого STAGE разное количество усреднений, поэтому в несколько блоков'''

    # Усреднение vz и плотности по симуляциям [STAGE 3]
    results = average_by_simulation(results, 9, N_SIMULATIONS)  # Усреднение плотности по симуляциям
    results = average_by_simulation(results, 13, N_SIMULATIONS)  # Усреднение температуры bias по симуляциям

    vz_list_st2 = results[0][3]  # для определения момента времени начала испарения
    d_list_st3 = results[0][9]
    t_bias_list_st3 = results[0][13]

    time_step_list = []
    coord_step_list = []  # Положение поверхности жидкости в каждый момент времени
    density_step_list = []  # Плотность поверхности жидкости в каждый момент времени
    t_bias_step_list = []  # Температура поверхности жидкости в каждый момент времени

    # Максимально допустимое изменение плотности внутри жидксти, превышение = межфазная граница

    for s in range(N_AVERAGES_st3 - 1):
        old_density = float(d_list_st3[s][N_left_side])
        is_find = False
        for m in range(N_CHUNKS):
            if is_find == False:
                if m >= N_left_side and m <= (N_CHUNKS - N_right_side):
                    current_density = float(d_list_st3[s][m])
                    if old_density - current_density > delta_density:
                        time_step_list.append(int((s + 1 + len(vz_list_st2) - 1) * 20000 * 0.005) / 1000)  # [ns]
                        coord_step_list.append(coord_list[0][m - 1])
                        density_step_list.append(d_list_st3[s][m - 1])
                        t_bias_step_list.append(t_bias_list_st3[s][m - 1])
                        old_density = current_density
                        is_find = True
                        continue
                    old_density = current_density
            else:
                continue

    # save txt
    file_name = 'interface_evolution.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      coord [nm]      density [kg/m3]      T_bias [K]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}   {}   {}\n'.format(time_step_list[i], coord_step_list[i], density_step_list[i], t_bias_step_list[i]))

    # save txt
    file_name = 'interface_coord.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      coord [nm]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], coord_step_list[i]))

    # save txt
    file_name = 'interface_density.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      density [kg/m3]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], density_step_list[i]))

    # save txt
    file_name = 'interface_temperature.txt'
    if "Linux" in platform.system():
        txt_file_dir = os.getcwd().replace('/Img/{}'.format(inspect.currentframe().f_code.co_name), '/Txt/') + file_name
    if "Windows" in platform.system():
        txt_file_dir = os.getcwd().replace('\\Img\\{}'.format(inspect.currentframe().f_code.co_name), '\\Txt\\') + file_name

    with open(txt_file_dir, 'w') as w:
        w.write('# TIMESTEP [ns]      T_bias [K]\n')
        for i in range(len(time_step_list)):
            w.write('{}   {}\n'.format(time_step_list[i], t_bias_step_list[i]))



if __name__ == '__main__':
    """Numbers of values: i -- Номер симуляции; k -- номер величины; s -- номер усредненния; m -- номер чанка 
    Example: value = results[i][k][s][m]
    coordinate = results[i][0][s][m]
    s2_density = results[i][1][s][m]
    s2_t = results[i][2][s][m]
    s2_vz = results[i][3][s][m]
    s2_p = results[i][4][s][m]
    s2_bias_t = results[5][k][s][m]
    s2_rdf_coord = results[6][k][s][m]
    s2_rdf_g = results[i][7][s][m]
    s2_rdf_l = results[i][8][s][m]
    s3_density = results[i][9][s][m]
    s3_t = results[i][10][s][m]
    s3_vz = results[i][11][s][m]
    s3_p = results[i][12][s][m]
    s3_bias_t_list = results[i][13][s][m]
    s4_density = results[i][14][s][m]
    s4_t = results[i][15][s][m]
    s4_vz = results[i][16][s][m]
    s4_p = results[i][17][s][m]
    s4_bias_t = results[i][18][s][m]
    """
    data = os_working()
    results = read_data(data)

    """ OUTPUT DATA """
    """ ЗАПУСКАТЬ ТОЛЬКО ПО ОДНОЙ ФУНКЦИИ!"""
    #test_lists(results)
    #plot_temperature_bias(results)
    #plot_t_bias_st2(results)
    #plot_t_bias_dens_st2(results)
    #delete_png()
    #plot_t_bias_dens_st2_st3(results)
    #plot_AVE_t_bias_dens_st2_st3(results, N_SIMULATIONS)  # Профиль температуры и плотности + усреднение
    #plot_AVE_pressure_dens_st2_st3(read_data(data), N_SIMULATIONS, N_left_side = 3, N_right_side = 2) # Профиль давления и плотности + усреднение
    #plot_AVE_massflow_dens_st2_st3(read_data(data), N_SIMULATIONS, N_left_side=0, N_right_side=0)  # Профиль потока массы и плотности + усреднение
    #plot_AVE_massflow_density_vz_time_in_gas(read_data(data), N_SIMULATIONS, N_left_side=50, N_right_side=5)  # Эволюция ВСЕХ МАКРОСКОПИЧЕСКИХ ВЕЛИЧИН в газе
    #AVE_profiles_by_time(results, N_SIMULATIONS)  # Усредненные по симуляциям и времени расчета профили
    #plot_AVE_RDF_L_G_st2(results, N_SIMULATIONS)  # Радиальная функция распределения для газа и жидкости
    #AVE_values_in_gas_st3(results, N_SIMULATIONS)  # Усредненные значения в ГАЗЕ по времени и симуляциям
    find_interface(results, N_SIMULATIONS, N_left_side=2, N_right_side=0, delta_density = 100)
