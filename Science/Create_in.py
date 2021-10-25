import os
import shutil
import platform

if "Linux" in platform.system():
    main_in_file = os.getcwd() + r'/in.MAIN'
    py_dir = os.getcwd() + r'/Py'
if "Windows" in platform.system():
    main_in_file = os.getcwd() + r'\\in.MAIN'
    py_dir = os.getcwd() + r'\\Py'




temperature_list = [90, 95, 100]
density_gas_list = [0.0074, 0.0114, 0.001686]
density_liquid_list = [1.3787, 1.3468, 1.313]
layer_thickness_list = [90, 140, 190, 240, 290, 340, 390]
simulations_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
seed_list = [1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999]


def in_file_name(temperature, thickness, simulation):
    name = 'in.T{}L{}S{}'.format(temperature, thickness, simulation)
    return name


def create_dirs(create_in_file):
    if "Linux" in platform.system():
        os.chdir(os.getcwd().replace('/CREATE_MAIN', ''))
    if "Windows" in platform.system():
        os.chdir(os.getcwd().replace('\\CREATE_MAIN', ''))
    t = 0
    for temperature in temperature_list:
        try:
            os.mkdir('T{}'.format(temperature))
        except:
            pass
        if "Linux" in platform.system():
            os.chdir(os.getcwd() + '/T{}'.format(temperature))
        if "Windows" in platform.system():
            os.chdir(os.getcwd() + '\\T{}'.format(temperature))
        l = 0
        for thickness in layer_thickness_list:
            try:
                if "Linux" in platform.system():
                    os.mkdir(r'{}/L{}'.format(os.getcwd(), thickness + 10))
                if "Windows" in platform.system():
                    os.mkdir(r'{}\\L{}'.format(os.getcwd(), thickness + 10))
            except:
                pass
            if "Linux" in platform.system():
                os.chdir(os.getcwd() + '/L{}'.format(thickness + 10))
            if "Windows" in platform.system():
                os.chdir(os.getcwd() + '\\L{}'.format(thickness + 10))
            s = 0
            for simulation in simulations_list:
                try:
                    if "Linux" in platform.system():
                        os.mkdir(r'{}/S{}'.format(os.getcwd(), simulation))
                    if "Windows" in platform.system():
                        os.mkdir(r'{}\\S{}'.format(os.getcwd(), simulation))
                except:
                    pass
                # os.chdir(os.getcwd() + 'S{}'.format(simulation))
                if create_in_file == True:
                    in_creation(t, l, s, temperature, thickness, simulation)
                s += 1
            l += 1
            if "Linux" in platform.system():
                os.chdir(os.getcwd().replace('/L{}'.format(thickness + 10), ''))
            if "Windows" in platform.system():
                os.chdir(os.getcwd().replace('\\L{}'.format(thickness + 10), ''))
            copy_py_img(thickness)
        if "Linux" in platform.system():
            os.chdir(os.getcwd().replace('/T{}'.format(temperature), ''))
        if "Windows" in platform.system():
            os.chdir(os.getcwd().replace('\\T{}'.format(temperature), ''))
        t += 1


def in_creation(t, l, s, temperature, thickness, simulation):
    filename = in_file_name(temperature, thickness, simulation)
    if "Linux" in platform.system():
        current_file = os.getcwd() + '/S{}/{}'.format(s+1, filename)
    if "Windows" in platform.system():
        current_file = os.getcwd() + '\\S{}\\{}'.format(s + 1, filename)
    with open(main_in_file, 'r') as r, open(current_file, 'w') as w:
        lines = r.readlines()
        for n_line in lines:
            if n_line.startswith('variable ZLiquid2'):
                temp_line = n_line.replace('390', '{}'.format(layer_thickness_list[l]))
                w.write(temp_line)
                continue
            if n_line.startswith('variable SEED'):
                temp_line = n_line.replace('1111', '{}'.format(seed_list[s]))
                w.write(temp_line )
                continue
            if n_line.startswith('variable rhoL'):
                temp_line = n_line.replace('1.2791', '{}'.format(density_liquid_list[t]))
                w.write(temp_line)
                continue
            if n_line.startswith('variable rhoG'):
                temp_line = n_line.replace('0.024', '{}'.format(density_gas_list[t]))
                w.write(temp_line)
                continue
            if n_line.startswith('variable T_All'):
                temp_line = n_line.replace('105', '{}'.format(temperature_list[t]))
                w.write(temp_line)
                continue
            w.write(n_line)


def copy_py_img(thickness):
    try:
        if "Linux" in platform.system():
            shutil.rmtree(os.getcwd() + '/L{}'.format(thickness+10) + '/Py')
        if "Windows" in platform.system():
            shutil.rmtree(os.getcwd() + '\\L{}'.format(thickness + 10) + '\\Py')
    except:
        pass
    if "Linux" in platform.system():
        shutil.copytree(py_dir, os.getcwd() + '/L{}'.format(thickness+10) + '/Py')
    if "Windows" in platform.system():
        shutil.copytree(py_dir, os.getcwd() + '\\L{}'.format(thickness + 10) + '\\Py')


create_dirs(create_in_file=False)


