import sys, os, logging

lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config
import redis

import utils
from utils import calibration
from drivers import driver

import time
import datetime
import json
from collections import defaultdict

##Example Control
#TSI-Heat_Check:
    #cooldown: 10                                      #minimum time between activating (seconds)
    #max_duration: 30                           #time after which it will automatically turn off
    #inputs:
        #Tempin: TSI-Temp 
    #entry_condition:
        #str: 'Tempin > 60'
        #type: REPETITION                         #REPETITION or PERIOD or INSTANTANEOUS
        #reps: 5
        #duration: 10                       #Repetitions-Seconds for REPETITION and Seconds for DURATION; INSTANTANEOUS does not use this field
    #exit_condition:
        #str: 'Tempin <= 40'                     #Condition to turn off Watcher action once its been activated, only used for LATCH persistence, cannot be true at same time as Condition
        #type: DURATION
        #duration: 8
    #action:
        #type: LOG                                  #if LOG put text, if WARNING put text (maybe color/flashing?), if WRITE write to a sensor on the vehicle:
        #message: 'TSI Temperature over 60'  

    #NOTE: these are not full configurations. Just examples of Action_Details for alternate Action_Type's

    #action:
        # type: WARNING
        # message: "msg1"
        # suggestion: "suggestion1"
        # priority: 5

    #action:
        # type: WRITE
        # sensor: sensorName
        # value: val

class Control:
    def __init__(self, configDict):
        self.active = False
        self.lastActive = 0
        self.cooldown = configDict.get('cooldown')
        self.maxDuration = configDict.get('max_duration')
        #list of strings of input sensor names
        inputs = configDict.get('inputs')

        #initializes entry condition attributes
        typ = configDict.get('entry_condition').get('type')
        if typ == 'INSTANTANEOUS':
            self.entryCondition = Instantaneous(configDict.get('entry_condition'), inputs)
        elif typ == 'DURATION':
            self.entryCondition = Duration(configDict.get('entry_condition'), inputs)
        elif typ == 'REPETITION':
            self.entryCondition = Repetition(configDict.get('entry_condition'), inputs)
        
        
        #initializes action attributes
        typ = configDict.get('action').get('type')
        if typ == 'LOG':
            self.action = Log(configDict.get('action'))
        elif typ == 'WARNING':
            self.action = Warning(configDict.get('action'))
        elif typ == 'WRITE':
            self.action = Write(configDict.get('action'))

        #optional attributes (must use "try" in case they are not there):

        #initializes exit condition attributes
        try:
            typ = configDict.get('exit_condition').get('type')
            if typ == 'INSTANTANEOUS':
                self.exitCondition = Instantaneous(configDict.get('exit_condition'), inputs)
            elif typ == 'DURATION':
                self.exitCondition = Duration(configDict.get('exit_condition'), inputs)
            elif typ == 'REPETITION':
                self.exitCondition = Repetition(configDict.get('exit_condition'), inputs)
        except:
            self.exitCondition = None
        
        #initializes max duration and cooldwon attributes
        try:
            self.maxDuration = configDict.get('max_duration')
        except:
            self.maxDuration = None
        try:
            self.cooldown = configDict.get('cooldown')
        except:
            self.cooldown = 0

    #returns boolean
    def checkEntryCondition(self):
        return (time.time() - self.lastActive) > self.cooldown and self.entryCondition.check()

    #returns boolean
    def checkExitCondition(self):
        if self.exitCondition is not None:
            return (self.maxDuration is not None and time.time() - lastActive > self.maxDuration) or self.exitCondition.check()
        else:
            return (self.maxDuration is not None and time.time() - lastActive > self.maxDuration) 

    #checks conditions and changes active/inactive state accordingly
    def update(self):
        if not self.active:
            print('CHECKING ENTRY CONDITION' + self.entryCondition.str)
            if self.checkEntryCondition():
                self.active = True
        else:
            print('CHECKING EXIT CONDITION')
            if self.checkExitCondition():
                self.active = False

        if self.active:
            print('ABOUT TO EXECUTE')
            self.action.execute()

class Condition:
    def __init__(self, configDict, inputs):
        self.str = configDict.get('str')
        self.inputs = inputs.values()
        for key in inputs:
            self.str = self.str.replace(key, inputs[key].replace('\n','')) #TODO: need to fix this
            
    #evaluates the condition string
    def evaluate(self):
        for i in self.inputs:
            try:
                if DataStorage[i] == 'no data': #will not trigger anything unless there is data for all inputs
                    return False
                condition = self.str.replace(i, DataStorage[i].replace('\n',''))
                print( 'about to evaluate ' + condition)
            except KeyError:
                return False
        return eval(condition)


class Instantaneous(Condition):
    def __init__(self, configDict, inputs):
        super().__init__(configDict, inputs)

    def check(self):
        return self.evaluate()

class Duration(Condition):
    def __init__(self, configDict, inputs):
        self.duration = configDict.get('duration')
        self.times = []
        super().__init__(configDict, inputs)
        

    def check(self):
        if self.evaluate():
            self.times.append(time.time()) 

            if self.times and self.times[-1] - self.times[0] > max_duration:
                return True

        else:
            self.times.clear()
            return False

class Repetition(Condition):
    def __init__(self, configDict, inputs):
        self.duration = configDict.get('duration')
        self.reps = configDict.get('reps')
        self.times = []
        super().__init__(configDict, inputs)

    def check(self):
        if self.evaluate():
            self.times.append(time.time())

            while self.times and self.times[-1] - self.times[0] > float(self.duration):
                self.times.pop(0)

            if len(self.times) > int(self.reps):
                return True
        return False


class Action:
    def __init__(self):
        pass
    

class Log(Action):
    def __init__(self, configDict):
        self.message = configDict.get('message')

    def execute(self):
        #log message to log
        pass

class Warning(Action):
    def __init__(self, configDict):
        self.message = configDict.get('message')
        self.suggestion = configDict.get('suggestion')
        self.priority = configDict.get('priority')

    def execute(self):
        warningTotal += 1
        warnings['warning'][warningTotal] = {'message':self.message, 'suggestion':self.message,'priority':self.priority}
        open('usr\etc\dashboard.json', 'w').close()
        with open('usr\etc\dashboard.json','a') as outfile:
            outfile.write(json.dumps(warnings))

class Write(Action):
    def __init__(self, configDict):
        self.sensor = configDict.get('sensor')
        self.value = configDict.get('value')

    def execute(self):
        print('Trying to execute WRITE action')
        driver.write(self.sensor, self.value)

def watch(message):
    split_key = message.split(':',1)
    sensor = split_key[0]
    val = split_key[1]
    relevantControls = ControlsDict[sensor]
    for control in relevantControls:
        print ('updating control ' + str(control))
        control.update()

#Setting up connection to Redis Server
Redisdata = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
data = Redisdata.pubsub()
data.subscribe('calculated_data')

allControls = config.get('Controls') #complete list of sensor configurations to make objects from
ControlsDict = defaultdict(list) #dictionary of (lists of) controls organized by the input sensor (key = sensor name)
DataStorage = {} #dictionary of current values of every sensor
# defaultControlDict = ControlsList.get('default_control')
warningTotal = 0
warnings = {}   


#Control object instantiation procedure
for controlString in allControls:
    configDict = allControls.get(controlString)
    control = Control(configDict)
    inputs = configDict.get('inputs').values()
    for i in inputs:
        ControlsDict[i].append(control) #stores controls under the sensor inputs they use
        #this is done because the Watcher looks for controls on incoming data inputs


#ACTUAL CODE THAT RUNS
while True:
    message = data.get_message()
    if (message and (message['data'] != 1 )):
        watch(message['data'])
    time.sleep(.01)
