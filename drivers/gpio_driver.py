##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Mithil Shah,Irwin Frimpong,Harrison Walker,Lia Chrysanthopoulos, Adam Tunnell                                    
## Last Updated : 05/11/2021 5:14 PM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: gpio_driver.py                                                 
## Description: GPIO Driver whcih contains write and read methods for GPIO pins              
#############################################################################################

import sys
import os
import redis
import time
import RPi.GPIO as GPIO

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config
import utils

# read method for GPIO Configured sensor to read from GPIO value with primary adress as GPIO pin number 
# @param Sensor - Sensor of Interest
def read(Sensor):
    try:
        GPIO.setmode(GPIO.BCM)
        sensor_pin_address = config.get('Sensors').get(str(Sensor)).get('primary_address')
        GPIO.setup(sensor_pin_address, GPIO.IN)
        if(GPIO.input(sensor_pin_address)):
            return 1
        else:
            return 0
    except IOError:
        time.sleep(.0001)

# write method for GPIO Configured sensor  
# @param Sensor - Sensor of Interest
# @param Value - Value to be written to GPIO pin
def write(Sensor, Value):
    try:
        GPIO.setmode(GPIO.BCM)
        sensor_pin_address = config.get('Sensors').get(str(Sensor)).get('primary_address')
        # GPIO.setup(sensor_pin_address,GPIO.OUT)
        # GPIO.output(sensor_pin_address,True)
        GPIO.setup(sensor_pin_address, GPIO.OUT)
        GPIO.output(sensor_pin_address, True)
        time.sleep(5)
        GPIO.cleanup()
    except IOError:
        time.sleep(.0001)
