import sys, os
import time

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

from drivers import driver
import config 

#Module to that holds methods to intialize the BNO-055 IMU 


def imu_reset():
    #IMU IN CONFIG MODE
    #print("IMU defined constant: " + str(config.get('IMU_Config_Constants').get('CONFIG_MODE'))) 
    driver.write('opr_mode_reg',config.get('IMU_Config_Constants').get('CONFIG_MODE'))
    try:
        driver.write('trigger_reg',0x20)
    except OSError:
        pass
    time.sleep(0.7)
    

def imu_config():
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