#!/usr/bin/python3
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
    #this should take in channel and bustype?
    def __init__(self):
        self.network = canopen.Network()
        # #eventually the following lines should take arguments from config
        can_info = config.get('bus_info').get('CAN')
        try:
            #set up CAN bus connection
            os.system('ip link set can0 down')
            os.system('ip link set can0 up type can bitrate 125000')

            self.network.connect(channel=can_info.get('channel'), bustype=can_info.get('bus_type'))
            self.connected = True

            nodes = config.get('can_nodes')
            for node in nodes:
                nodeData = nodes.get(node)
                self.network.add_node(nodeData['id'], lib_path + '/utils/eds-files/' + nodeData['eds_file'])
            '''
            # To do this new procedure, the CAN part of the config must look like this
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
            
            #ensure nodes are connected
            # self.network.scanner.search()
            # time.sleep(1)
            # print("Connected Nodes:")
            # for node_id in self.network.scanner.nodes:
            #     print("Found node %d!" % node_id)

            allSensors = config.get('Sensors')
            self.sdoDict = {}
            for sensorName in allSensors:
                sensorDict = allSensors.get(sensorName)
                if sensorDict['bus_type'] == 'CAN':
                    #DEBUG:
                    print(sensorName)
                    print(sensorDict)
                    # print config.get('Sensors').get(sensorDict)
                    if 'nmt' not in sensorName:
                        self.sdoDict[sensorName] = self.configure_sdo(sensorName,sensorDict)
                    #DEBUG:
                    # print('sdoDict =')
                    # print(sdoDict)]
            print('Made it here for some reason')

        except OSError: #can.CanError is an OSError
            self.connected = False
            print('CAN Bus not connecting!')
            return None
 

    def __del__(self):
        #UNCOMMENT THIS FOR WORKING VERSION
        self.network.disconnect()

    def read(self,sensorName):
        #for now this is a redundant step, but if we use other CAN-subprotocols
        #or other canOpen structures, we would want to do some decision making here
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
        return self.sdoDict[sensorName].phys

    def read_nmt(self,sensorName):
        #sensor name is composed of the node name and the value name
        [nodeName, *valueName] = sensorName.split('_')
        #get node ID from config
        nodeNum = config.get('can_nodes').get(nodeName)
        #select node on network
        node = self.network[nodeNum]

        if 'state' in sensorName:
            return node.nmt.state
        
    #using SDOs for now
    def write_sdo(self,sensorName, value):
        self.sdoDict[sensorName].phys = value

    def write_nmt(self,sensorName, value):
        #sensor name is composed of the node name and the value name
        [nodeName, *valueName] = sensorName.split('_')
        #get node ID from config
        nodeNum = config.get('can_nodes').get(nodeName)
        #select node on network
        node = self.network[nodeNum]

        if 'state' in sensorName:
            node.nmt.state(value)

    def read_pdo(self,sensorName):
        #dummy method contents
        pass
    
    #write_pdo method is not applicable because it's only used to get data from devices

    def configure_sdo(self, sensorName, sensorDict):
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
    