##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Irwin Frimpong,Harrison Walker,Lia Chrysanthopoulos, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/11/2021 5:14 PM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: rtc_setup.py                                                 
## Description: RTC Setup Module to set Pi time to RTC time in the event when time 
##              synchronizing via an interenet connection isnt feasible              
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

clk_id = time.CLOCK_REALTIME 

def set_RTCtime():
#Setting Raspberry Pi Time to RTC Time 
    try:
        time.clock_settime(clk_id, driver.read('rtc_time'))
    except TypeError:
        time.sleep(0.0001)

## Methods to Configure the Pi time to RTC on boot
def rtc_pitimesteup():
    t = time.clock_gettime(clk_id)
    try:
        if (t < driver.read('rtc_time')): 
            set_RTCtime()
    except TypeError:
        time.sleep(0.0001)
        