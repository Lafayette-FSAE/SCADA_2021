#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Lia Chrysanthopoulos, Mithil Shah,Irwin Frimpong                                   
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: can_scan.py                                                 
## Description: This script is meant to detect and display info for all available nodes currently on the CAN bus
##              for debug purposes  
#############################################################################################

import sys, os
import time
import canopen

#Importing the config file
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'
#this is temporary, just for testing
local_path = '../utils'

sys.path.append(lib_path)
sys.path.append(config_path)
sys.path.append(local_path)

from drivers import can_driver

cd = can_driver.CanDriver()
network = cd.network

os.system('sudo ifconfig can0 txqueuelen 1000')
#ensure nodes are connected
network.scanner.search()
time.sleep(1)
print("Connected Nodes:")
for node_id in network.scanner.nodes:
    print("Found node %d!" % node_id)
    print('NODE %d INFORMATION:' % node_id)
    node = network[node_id]
    for obj in node.object_dictionary.values():
        print('0x%X: %s' % (obj.index, obj.name))
        if isinstance(obj, canopen.objectdictionary.Record):
            for subobj in obj.values():
                print('  %d: %s' % (subobj.subindex, subobj.name))