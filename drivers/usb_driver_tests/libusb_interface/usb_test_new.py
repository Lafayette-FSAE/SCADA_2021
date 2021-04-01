import sys, os
#Importing the config file
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'
#this is temporary, just for testing
local_path = '../utils'

sys.path.append(lib_path)
sys.path.append(config_path)
sys.path.append(local_path)

import config

import ctypes
import pathlib

if __name__ == "__main__":
    # Load the shared library from this folder into ctypes
    libname = pathlib.Path().absolute() / "usb-7204.so"
    c_lib = ctypes.CDLL(libname)
    # Set the return type to double
    c_lib.readChannel.restype = ctypes.c_double


channel = 0
result = c_lib.readChannel(ctypes.c_uint8(channel))

