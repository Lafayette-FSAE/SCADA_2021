#!/usr/bin/python3
import sys, os
import time
import smbus

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

from drivers import driver
import utils
from utils import rtc_setup
import config
import redis

#Setting Up I2C Bus Connection 
bus = smbus.SMBus(1) ##Currently On Bus 3 with clock stretching 

#Setting up connectiion to Redis Server
Redisdata = redis.Redis(host='localhost', port=6379, db=0)
data = Redisdata.pubsub()
data.subscribe('raw_data')

rtc_setup.set_RTCtime()

#Local Dictionary for Sensor Period Count
SensorList = config.get('Sensors')

last_sampled = {}
sample_period = {}
for key in config.get('Sensors'):
    sample_period[key] = SensorList.get(key).get('sample_period')
    last_sampled[key] = time.time()

####### Methods to Configure BNO055 IMU #######
onSetup = False  #Boolean var used to peform imu setup on startup

def imu_reset():
    #IMU IN CONFIG MODE
    print("IMU defined constant: " + str(config.get('IMU_Config_Constants').get('CONFIG_MODE'))) 
    driver.write('opr_mode_reg',config.get('IMU_Config_Constants').get('CONFIG_MODE'))
    try:
        driver.write('trigger_reg',0x20)
    except OSError:
        pass
    time.sleep(0.7)
    

def imu_setup():
    #Debuggin: 
    opr_mode_reg_read = driver.read('opr_mode_reg')
    # print("Value of Opr_Mode: " + str(opr_mode_reg_read))
   # print( "SensorList Dictionary: " + str(SensorList))
    global onSetup # Python UnboundLocalError fix
   # if (opr_mode_reg_read == 0 or opr_mode_reg_read != 12): #If its in Config Mode and not in NDOF mode, want to configure it
    if (opr_mode_reg_read == 0 or (bool(onSetup) == False)):
        onSetup = True #OnSetup has been achieved 
        imu_reset()
        driver.write('power_reg',config.get('IMU_Config_Constants').get('POWER_NORMAL'))
        driver.write('page_reg',0x00)
        driver.write('trigger_reg',0x00)
        driver.write('acc_config_reg',config.get('IMU_Config_Constants').get('ACCEL_4G'))
        driver.write('gyro_config_reg',config.get('IMU_Config_Constants').get('GYRO_2000_DPS'))
        driver.write('mag_config_reg',config.get('IMU_Config_Constants').get('MAGNETOMETER_20HZ'))
        time.sleep(0.01)
    
        ##Setting IMU TO NDOF MODE
        driver.write('opr_mode_reg',config.get('IMU_Config_Constants').get('NDOF_MODE'))
        time.sleep(0.7)

## Methods to Configure the Pi time to RTC on boot
def rtc_pitimesteup():
    clk_id = time.CLOCK_REALTIME
    t = time.clock_gettime(clk_id)

    if (t < driver.read('rtc_time')): 
        rtc_setup.set_RTCtime()
        time.sleep(1)


while True: 
    #for Sensors: <-- needs to be name of list of sensors
    # milliseconds = int(time()*1000)

    ## IMU Setup
    imu_setup()

    ## RTC Setup
    rtc_pitimesteup()

    # Reading
    for sensorName in SensorList :
        if(time.time() - last_sampled[sensorName] > sample_period[sensorName] and float(sample_period[sensorName]) != 0.0):
            
            # print('SENSOR NAME IS ' + sensorName + 'and its type is')
            # print(type(sensorName))

            #Appending sensor name to sensor value for distinction in redis database
            key = '{}:{}'.format(sensorName, driver.read(sensorName))
            #Python String Method that makes everything lowercase
            key = key.lower()
            # print(key)
            #Putting Sensor Data into redis channel
            Redisdata.publish('raw_data',key)
            last_sampled[sensorName] = time.time()