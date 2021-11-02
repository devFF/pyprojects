# Description:
The program for determining the weather forecast in Russian cities.
![Screenshot](Interface.png)

# Working with source code:
1) Sign up and generate API key: https://home.openweathermap.org/api_keys
2) Create API.txt in the directory of the py file and insert the API key into it
3) For the correct work of the source, execute: 
* ```pip3 install lxml```
* ```sudo apt install font-manager```
* ```sudo apt-get install msttcorefonts -qq```
* ``` rm -r ~/.cache/matplotlib```

# To build source code:

1) To fix bug with certificate for library requests:

1.1) create a hook-requests.py file in PyInstaller\hooks\ for the requests lib containing
```Python
from PyInstaller.utils.hooks import collect_data_files
# Get the cacert.pem
datas = collect_data_files('requests')```

