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
# import usb_driver

# print('Reading from USB torque sensor:')
# print(usb_driver.read('usb_torque'))

from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType,
                   AiInputMode, Range, AInFlag)

try:
    # Get a list of available devices
    devices = get_daq_device_inventory(InterfaceType.USB)
    # Create a DaqDevice Object and connect to the device
    with DaqDevice(devices[0]) as daq_device:
        # Get AiDevice and AiInfo objects for the analog input subsystem
        ai_device = daq_device.get_ai_device()
        ai_info = ai_device.get_info()

        # Read and display voltage values for all analog input channels
        for channel in range(ai_info.get_num_chans()):
            data = ai_device.a_in(channel, AiInputMode.SINGLE_ENDED,
                                  Range.BIP10VOLTS, AInFlag.DEFAULT)
            print('Channel', channel, 'Data:', data)

except: #ULException as e:
    print('\nERROR')#, e)  # Display any error messages