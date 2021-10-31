# Building projects into executable files for Windows and Linux
# 1) Install pywin32 and pyinstaller:
```
pip install pypiwin32  # FOR WINDOWS ONLY !!!
```
```
pip install pyinstaller
```

# 2) Checking correctness of the installation
```
pyinstaller --version
```

# 3) Syntax:
```
pyinstaller [options] script [script ...] | specfile
```

# 4) Useful options:
--onefile # build project in one file

--windowed # show console 

--noconsole 

--icon=icon_file.ico # add ico

--add-data "temp\file_name1.txt;file_name2.png" # add extra files in executable file

# 5) Example:
```
pyinstaller --onefile --noconsole  GUI_calc.py
```

