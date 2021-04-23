import sys, os
import time

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

from drivers import driver
import config 

#Setting Raspberry Pi Time to RTC Time 
clk_id = time.CLOCK_REALTIME 
time.clock_settime(clk_id, driver.read('rtc_time'))