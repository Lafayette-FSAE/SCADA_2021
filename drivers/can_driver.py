#!/usr/bin/python3
##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Irwin Frimpong,Lia Chrysanthopoulos, Mithil Shah                                 
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: can_driver.py                                                 
## Description: CAN driver contains read and write methods for interfacing with sensors on the
##  vehicle using the CANopen protocol. Unlike the other drivers in SCADA, the CAN Driver is
##  written as an object because I thought it would be easier to keep track of variables that way.
#############################################################################################

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
import redis
import can
import canopen
import time



# open a connection to the redis server where we will
#  be writing data
#data = redis.Redis(host='localhost', port=6379, db=0)

class CanDriver:
    
    def __init__(self):
        """!
        Constructor method for the CAN Driver. Connects to the network and sets up
        SDO objects to be used to read/write sensors.

        takes in no parameters
        """

        #initializes CAN network
        self.network = canopen.Network()
        #retrieves CAN-relevant info from config
        can_info = config.get('bus_info').get('CAN')
        try:
            #set up CAN bus hardware connection using command line
            os.system('ip link set can0 down')
            os.system('ip link set can0 up type can bitrate 125000')

            #uses config values to set up CAN bus connection for our particular setup
            self.network.connect(channel=can_info.get('channel'), bustype=can_info.get('bus_type'))
            #if it makes it here without throwing an error, the CAN bus is working!
            self.connected = True

            #retrieves node information from config
            nodes = config.get('can_nodes')
            #adds individual CAN devices to the network according to values in config.
            for node in nodes:
                nodeData = nodes.get(node)
                self.network.add_node(nodeData['id'], lib_path + '/utils/eds-files/' + nodeData['eds_file'])
            '''
            # To do this procedure, the CAN part of the config must look like this
            can_nodes:
                motor:
                    id: 1
                    eds_file: '[nodeId=001]eds_eDrive150.eds'
                tsi:
                    id: 3
                    eds_file:
                pack1:
                    id: 4
                    eds_file: 'Pack.eds'
                pack2: 
                    id: 5
                    eds_file: 'Pack.eds'
            '''
            
            #ensure nodes are connected, this is for debugging
            # self.network.scanner.search()
            # time.sleep(1)
            # print("Connected Nodes:")
            # for node_id in self.network.scanner.nodes:
            #     print("Found node %d!" % node_id)

            #The rest of this method sets up the CAN Driver for our implementation by 
            #creating SDO objects and adding them to a dictionary that can be called
            #during runtime to read the sensors these SDO objects bind to
            allSensors = config.get('Sensors')
            self.sdoDict = {}

            for sensorName in allSensors:
                #looks at a sensor in config and checks if it's CAN
                sensorDict = allSensors.get(sensorName)
                if sensorDict['bus_type'] == 'CAN':
                    # #DEBUG:
                    # print(sensorName)
                    # print(sensorDict)

                    #if it is CAN, configures an SDO object for it
                    if 'nmt' not in sensorName:
                        self.sdoDict[sensorName] = self.configure_sdo(sensorName,sensorDict)
                    #DEBUG:
                    # print('sdoDict =')
                    # print(sdoDict)]
        except OSError: #can.CanError is an OSError
            #You will only get a CanError if there is an issue connecting to the CAN bus, so
            #this will set it up to do nothing when attempting to read CAN instead of producing errors
            self.connected = False
            print('CAN Bus not connecting!')
            return None
 
    def __del__(self):
        """!
        Destructor method for CAN Driver. Disconnects from the CAN bus to prevent errors

        takes in no parameters
        """
        self.network.disconnect()

    def read(self,sensorName):
        """!
        Method to read values from CAN sensors. Calls the protocol-specific read method (sdo or nmt)

        @param sensorName The name of the sensor to be read (as defined in config)
        """
        #for now this is a redundant step, but if we use other CAN-subprotocols
        #or other canOpen structures that are not SDO, we would want to do some decision making here
        if self.connected:
            try:
                #WHY DOES THIS NOT WORK
                if 'nmt' in str(sensorName):
                #if sensorName.find('nmt') != -1:
                    return self.read_nmt(sensorName)
                else:
                    return self.read_sdo(sensorName)
            except OSError:
                return None
        else:
            return None

    def write(self,sensorName, value):
        """!
        Method to write  values to CAN sensors. Calls the protocol-specific write method (sdo or nmt)
        
        @param sensorName The name of the sensor to be written to (as defined in config)
        @param value The value to be written to this sensor
        """

        #for now this is a redundant step, but if we use other CAN-subprotocols
        #or other canOpen structures, we would want to do some decision making here
        if self.connected:
            try:
                if 'nmt' in sensorName:
                    self.write_nmt(sensorName, value)
                else: 
                    self.write_sdo(sensorName, value)
            except OSError:
                pass

    #using SDOs for now
    def read_sdo(self,sensorName):
        """!
        Method to read "real" values from CAN sensors using SDO. Calls "phys" attribute of SDO object
        which should get the calibrated (real) value from the sensor if the sensor supports it
        If not supported, phys will return the raw value

        @param sensorName The name of the sensor to be read (as defined in config)
        """
        return self.sdoDict[sensorName].phys

    def read_nmt(self,sensorName):
        """!
        Method to read network state values from CAN using NMT. Calls "state" attribute of NMT object
        which should get the string representing the state value.
        Note: this method has never worked thus far.

        @param sensorName The name of the sensor to be read (as defined in config)
        """
        #sensor name is composed of the node name and the value name
        [nodeName, *valueName] = sensorName.split('_')
        #get node ID from config
        nodeNum = config.get('can_nodes').get(nodeName)
        #select node on network
        node = self.network[nodeNum]

        #read
        if 'state' in sensorName:
            return node.nmt.state
        
    
    def write_sdo(self,sensorName, value):
        """!
        Method to write values to CAN sensors using SDO protocol.
        Sets the value of "phys" (the calibrated value) in the object dictionary to the given value
        
        @param sensorName The name of the sensor to be written to (as defined in config)
        @param value The value to be written to this sensor
        """
        self.sdoDict[sensorName].phys = value

    def write_nmt(self,sensorName, value):
        """!
        Method to change network state of CAN nodes using NMT protocol.
        Sets the value of "phys" (the calibrated value) in the object dictionary to the given value
        
        @param sensorName The name of the state object to be written to (as defined in config)
        @param value The state value to be written to this sensor
        """
        #sensor name is composed of the node name and the value name
        [nodeName, *valueName] = sensorName.split('_')
        #get node ID from config
        nodeNum = config.get('can_nodes').get(nodeName)
        #select node on network
        node = self.network[nodeNum]

        #writes
        if 'state' in sensorName:
            node.nmt.state(value)

    def read_pdo(self,sensorName):
        """!
        Method to read values from CAN sensors using PDO.
        Not yet implemented, might not need to be since SDO works just fine.

        @param sensorName The name of the sensor to be read (as defined in config)
        """
        #dummy method contents
        pass
    
    #write_pdo method is not applicable because it's only used to get data from devices

    def configure_sdo(self, sensorName, sensorDict):
        """!
        Configures a sensor to be read/written using SDO using the constructor for SDO
        objects from the CANopen python library with attributes from config

        @param sensorName The name of the sensor to be read (as defined in config)
        @param sensorDict Dictionary of attributes describing the sensor
        """
        #sensor name is composed of the node name and the value name
        [nodeName, *valueName] = sensorName.split('_')
        #get node ID from config
        nodeNum = config.get('can_nodes').get(nodeName).get('id')
        #select node on network
        node = self.network[nodeNum]

        #creates SDO object that will communicate with the sensor
        if sensorDict['secondary_address'] == None:
            new_sdo = node.sdo[sensorDict['primary_address']]
        else:
            new_sdo = node.sdo[sensorDict['primary_address']][sensorDict['secondary_address']]
        return new_sdo
    