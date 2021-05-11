##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Irwin Frimpong,Harrison Walker,Lia Chrysanthopoulos, Adam Tunnell, Mithil Shah                                  
## Last Updated : 05/11/2021 5:14 PM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: imu_setup.py                                                 
## Description: imu_setup module holds methods to configure the IMU at startup              
#############################################################################################

import sys, os
import time

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

from drivers import driver
import config 

onSetup = False  #Boolean var used to peform imu setup on startup

def imu_reset():
    #IMU IN CONFIG MODE
    driver.write('opr_mode_reg',config.get('IMU_Config_Constants').get('CONFIG_MODE'))
    try:
        driver.write('trigger_reg',0x20)
    except OSError:
        pass
    time.sleep(0.7)
    
#imu_config method used to intialize the BNO-055 IMU on startup
def imu_config():
    opr_mode_reg_read = driver.read('opr_mode_reg')
    global onSetup # Python UnboundLocalError fix

    if (opr_mode_reg_read == 0 or (bool(onSetup) == False)):
        onSetup = True #OnSetup has been achieved 
        imu_reset()
        driver.write('power_reg',config.get('IMU_Config_Constants').get('POWER_NORMAL'))
        driver.write('page_reg',0x00) # Setting Page to 0
        driver.write('trigger_reg',0x00)
        time.sleep(0.01)

        #Setting PageReg to 1 to configure mag,gyro,and acceleromoter
        driver.write('page_reg',0x01)
        driver.write('acc_config_reg',config.get('IMU_Config_Constants').get('ACCEL_4G'))
        driver.write('gyro_config_reg',config.get('IMU_Config_Constants').get('GYRO_2000_DPS'))
        driver.write('mag_config_reg',config.get('IMU_Config_Constants').get('MAGNETOMETER_20HZ'))
        time.sleep(0.01)

        #Switching Back to page 0
        driver.write('page_reg',0x00) # Setting Page to 0
    
        ##Setting IMU TO NDOF MODE
        driver.write('opr_mode_reg',config.get('IMU_Config_Constants').get('NDOF_MODE'))
        time.sleep(0.7)