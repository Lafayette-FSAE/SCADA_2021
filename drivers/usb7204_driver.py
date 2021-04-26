#!/usr/bin/python3
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

#BELOW ARE FROM OLD IMPLEMENTATION

# allSensors = config.get('Sensors')
# usbDevices = {} # holds all the USB device python objects
# endPoints = {} #holds all the endpoint addresses

# def write(sensorName, value):
#     pass

# def read(sensorName):
#     # parameters here are the endpoint address, byte length and timeout, respectively
#     val = usbDevices[sensorName].read(endPoints[sensorName], 1024,10000) #byte length for torque is 64
#     print(len(val))
#     return val

# def configure_sensor(sensorName, sensorDict):
#     vendorID = sensorDict.get('primary_address')
#     productID = sensorDict.get('secondary_address')
    
#     #stuff from pyusb github example
#     dev =  usb.core.find(idVendor=vendorID, idProduct = productID)
#     if dev is None:
#         raise ValueError('Device not found')

#     #from YouTube video tutorial
#     ep = dev[0].interfaces()[0].endpoints()[0]
#     i = dev[0].interfaces()[0].bInterfaceNumber
#     dev.reset()

#     if dev.is_kernel_driver_active(i):
#         dev.detach_kernel_driver(i)

#     dev.set_configuration()
#     eaddr = ep.bEndpointAddress
#     #end YouTube tutorial

#     endPoints[sensorName] = eaddr

#     # dev.set_configuration()

#     # cfg = dev.get_active_configuration()
#     # intf = cfg[(0,0)]

#     # ep = usb.util.find_descriptor(
#     #     intf,
#     #     # match the first OUT endpoint
#     #     custom_match = \
#     #     lambda e: \
#     #         usb.util.endpoint_direction(e.bEndpointAddress) == \
#     #         usb.util.ENDPOINT_OUT)

#     return dev

# for sensorName in allSensors:
#     sensorDict = allSensors.get(sensorName)
#     if sensorDict['bus_type'] == 'USB720':
#         usbDevices[sensorName] = configure_sensor(sensorName, sensorDict)
#         print('just added usb device called' + sensorName)