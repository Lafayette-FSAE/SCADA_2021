#!/usr/bin/python3
import sys, os
import time

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import utils
import config

from drivers import i2c_driver, emulated_driver
from drivers import can_driver   #UNCOMMENT
from drivers import usb7204_driver
from drivers import gpio_driver

SensorList = config.get('Sensors')
emulating = config.get('emulation')

#set up CAN bus connection
# os.system('ip link set can0 down')
# os.system('ip link set can0 up type can bitrate 125000')

can_drive = can_driver.CanDriver() #TODO: Fix this ambiguous ass name  ##UNCOMENNETTTT!!!

#Set RTC Time to Sys Time 
#os.system ()


# Method to read from the sesnor objects depending on protocol                
def read(Sensor):
#make it look at the folder for what protocol to use
    sensor_protocol = SensorList.get(str(Sensor)).get('bus_type')
    if(sensor_protocol == 'I2C'):
        data = i2c_driver.read(Sensor)
    elif(sensor_protocol =='CAN'):
        data = can_drive.read(Sensor)
    elif(sensor_protocol == 'USB7204'):
        data= usb7204_driver.read(Sensor)
    elif(sensor_protocol == 'GPIO'):
        data= gpio_driver.read(Sensor)
    elif(sensor_protocol == 'VIRTUAL'):
        data= 0
    elif(emulating and sensor_protocol == 'EMULATED'):
        data = emulated_driver.read(Sensor)
    else:
        return 'Sensor Protocol Not Found'
    #  #Redis Write Command 

    if(data == None): #Sensor is either unavialble or disconnected 
        data = 'no data'
        
    return data


#Write to sensor 
def write(Sensor,Value):
    #Debuggin
    print( "Sensor: " + str(Sensor) + " Value: " + str(Value))
    sensor_protocol = SensorList.get(str(Sensor)).get('bus_type')
    print('Protocol: ' + sensor_protocol)
    if(sensor_protocol == 'I2C'):
        i2c_driver.write(Sensor, Value)
    elif(sensor_protocol =='CAN'):
        can_drive.write(Sensor,Value)
    elif(sensor_protocol == 'USB'):
        usb7204_driver.write(Sensor,Value)
    elif(emulating and sensor_protocol == 'EMULATED'):
        emulated_driver.write(Sensor,Value)
    elif(sensor_protocol == 'GPIO'):
        data= gpio_driver.write(Sensor,Value)
    else:
        return 'Sensor Protocol Not Found'


# while True: 
#     #for Sensors: <-- needs to be name of list of sensors
#     # milliseconds = int(time()*1000)
#     for sensorName in SensorList :
#         if(time.time() - last_sampled[sensorName] > sample_period[sensorName] and float(sample_period[sensorName]) != 0.0):
#             #Appending sensor name to sensor value for distinction in redis database
#             key = '{}:{}'.format(sensorName, read(sensorName))
#             #Python String Method that makes everything lowercase
#             key = key.lower()
#             print(key)
#             #Putting Sensor Data into redis channel
#             Redisdata.publish('raw_data',key)
#             last_sampled[sensorName] = time.time()
