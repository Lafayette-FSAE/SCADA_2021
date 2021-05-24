#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Lia Chrysanthopoulos, Mithil Shah,Irwin Frimpong                                   
## Last Updated : 05/24/2021 1:08 PM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: usb7024_driver.py                                                 
## Description: The usb7024_driver module contains read and write methods for usb7024 board            
#############################################################################################
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
import redis
# import usb.core
# import usb.util
import time
import pathlib
import ctypes


# Load the shared library from this folder into ctypes
libname = pathlib.Path(__file__).parent.absolute() / "usb_dependencies/mcc-libusb/libmccusb.so"
c_lib = ctypes.CDLL(libname)
# Set the return type of imported C methods
c_lib.readChannel.restype = ctypes.c_double
c_lib.setup_usb7204.restype = ctypes.c_bool

# use imported C method to setup USB7204 board and set USB driver "connected" status
connected = c_lib.setup_usb7204()


allSensors = config.get('Sensors')
channels = {} # holds the channel numbers corresponding to devices on USB-7204 board

def read(sensorName):
    if connected:
        channel = channels[sensorName]
        return c_lib.readChannel(ctypes.c_uint8(channel))
    return None

#Note: value must be a VOLTAGE value between 0 and 5.0
#Note: in our current hardware configuration (in which we use the USB-7204 DAQ board for data aquisition only)
#we would never realistically use this method
def write(sensorName, value):
    if connected:
        channel = channels[sensorName]
        c_lib.writeToChannel(ctypes.c_uint8(channel), ctypes.c_float(value))


#setup code to get config info (channel for reading device)
for sensorName in allSensors:
    sensorDict = allSensors.get(sensorName)
    if sensorDict['bus_type'] == 'USB7204':
        channels[sensorName] = int(sensorDict.get('primary_address'))
        print('just added usb device called' + sensorName)

