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
    time.clock_settime(clk_id, driver.read('rtc_time'))

## Methods to Configure the Pi time to RTC on boot
def rtc_pitimesteup():
    t = time.clock_gettime(clk_id)

    if (t < driver.read('rtc_time')): 
        set_RTCtime()
        time.sleep(1)