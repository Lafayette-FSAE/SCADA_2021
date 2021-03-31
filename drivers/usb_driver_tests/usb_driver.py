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
import usb.core
# import usb.util
import time

allSensors = config.get('Sensors')
usbDevices = {} # holds all the USB device python objects
endPoints = {} #holds all the endpoint addresses

def write(sensorName, value):
    pass

def read(sensorName):
    # parameters here are the endpoint address, byte length and timeout, respectively
    val = usbDevices[sensorName].read(endPoints[sensorName], 1024,10000) #byte length for torque is 64
    print(len(val))
    return val

def configure_sensor(sensorName, sensorDict):
    vendorID = sensorDict.get('primary_address')
    productID = sensorDict.get('secondary_address')
    
    #stuff from pyusb github example
    dev =  usb.core.find(idVendor=vendorID, idProduct = productID)
    if dev is None:
        raise ValueError('Device not found')

    #from YouTube video tutorial
    ep = dev[0].interfaces()[0].endpoints()[0]
    i = dev[0].interfaces()[0].bInterfaceNumber
    dev.reset()

    if dev.is_kernel_driver_active(i):
        dev.detach_kernel_driver(i)

    dev.set_configuration()
    eaddr = ep.bEndpointAddress
    #end YouTube tutorial

    endPoints[sensorName] = eaddr

    # dev.set_configuration()

    # cfg = dev.get_active_configuration()
    # intf = cfg[(0,0)]

    # ep = usb.util.find_descriptor(
    #     intf,
    #     # match the first OUT endpoint
    #     custom_match = \
    #     lambda e: \
    #         usb.util.endpoint_direction(e.bEndpointAddress) == \
    #         usb.util.ENDPOINT_OUT)

    return dev

for sensorName in allSensors:
    sensorDict = allSensors.get(sensorName)
    if sensorDict['bus_type'] == 'USB':
        usbDevices[sensorName] = configure_sensor(sensorName, sensorDict)
        print('just added usb device called' + sensorName)