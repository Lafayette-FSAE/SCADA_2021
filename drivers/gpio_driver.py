import sys
import os
import config
#import smbus
import redis
import utils
import time
import RPi.GPIO as GPIO
# sudo apt-get install python-rpi.gpio
# nano ledexample.py

# General method to read from GPIO value with primary adress as GPIO pin number


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

# General method to write to GPIO value


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
