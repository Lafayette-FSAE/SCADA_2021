#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Lia Chrysanthopoulos, Mithil Shah,Irwin Frimpong                                   
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: watcher.py                                                 
## Description: Watcher module used for Active System Control of SCADA system
## This object-oriented module checks for threshold conditions on sensors as their data comes
## in and responds to them with logging, warning, or sensor writing as defined in config.                
#############################################################################################
import sys, os, logging

lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config
import redis

import utils
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
    """!
    Controls are the structures that make up the Watcher.
    Each Control consists of an entry condition (which activates the Control),
    an action (what the Control does), and several other optional attributes 
    that further restrict how the Control can be activated.

    The Conditions and Actions that a Control contains are implemented as objects themselves.
    """

    def __init__(self, configDict):
        """!
        Constructor for Controls.
        Creates the Control object based on its description in Config

        @param configDict Dictionary of attributes that describe the Control
        """
        self.active = False
        self.lastActive = 0
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

        #the follwoing are optional attributes (must use "try" in case they are not there):

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
        """!
        Checks whether a control should be activated.
        In order to be activated, the Control must not have been activated for the duration of its cooldown
        AND the entry condition must be fulfilled.

        takes no parameters.
        """
        if self.cooldown is not None:
            return ((time.time() - self.lastActive) > self.cooldown and self.entryCondition.check())
        else:
            return self.entryCondition.check()
    
    def checkExitCondition(self):
        """!
        Checks whether a control should be deactivated.
        In order to be deactivated, the Control must be active for its max duration
        OR the exit condition must be fulfilled.

        takes no parameters.
        """
        if self.exitCondition is not None:
            return (self.maxDuration is not None and time.time() - self.lastActive > self.maxDuration) or self.exitCondition.check()
        else:
            return (self.maxDuration is not None and time.time() - self.lastActive > self.maxDuration) 

    def update(self):
        """!
        Updates the state (active or inactive) of a Control.
        Executes the Control's action if it is active.
        This method is run whenever the sensors that activate the control have new data.

        takes no parameters.
        """
        if not self.active:
            # print('CHECKING ENTRY CONDITION' + self.entryCondition.str)
            if self.checkEntryCondition():
                self.active = True
        else:
            # print('CHECKING EXIT CONDITION')
            if self.checkExitCondition():
                self.active = False
                self.lastActive = time.time()
                if type(self.action) is Warning:
                    self.action.unexecute()

        if self.active:
            # print('ABOUT TO EXECUTE')
            self.action.execute()
        
        

class Condition:
    """!
    Super class for conditions that activate/deactivate a Control. There are 3 subclasses:
    Instantaneous (which is fulfilled if a threshold is met once),
    Duration (which is fulfilled if a threshold is met for a given duration), and 
    Repetition (which is fulfilled if a threshold is met a given number of times in a given duration)
    """

    def __init__(self, configDict, inputs):
        """!
        Generic constructor method used for all Conditions.
        Assigns attributes that all types of Conditions use: 
        str (the string representation of the threshold condition evaluated as true/false)
        inputs (the sensors whose readings can trigger the Control)

        @param configDict Dictionary of attributes that describe the Condition
        @param inputs Dictionary within configDict that deals with the sensors the Condition "watches"
        """
        self.str = configDict.get('str')
        self.inputs = inputs.values()
        for key in inputs:
            self.str = self.str.replace(key, inputs[key].replace('\n','')) #TODO: need to fix this

    def evaluate(self):
        """!
        Evaluates the string representing a Conditions.
        Replaces names of sensors in the condition string with actual values for those sensors
        then runs built-in Python eval() method to evaluate the string true or false

        takes no paramters.
        """
        for i in self.inputs:
            inputData = DataStorage[i]
            try:
                if inputData == 'no data': #will not trigger anything unless there is data for all inputs
                    return False
                elif not inputData.isdecimal(): #for string variables i.e. states
                    inputData = '"' + inputData + '"' 
                condition = self.str.replace(i, inputData.replace('\n',''))
                # print( 'about to evaluate ' + condition)
            except KeyError: #if no data exists (not even a 'no data' string) for any of the sensors yet
                return False
        return eval(condition)


class Instantaneous(Condition):
    """!
    Sub class of Condition that is fulfilled if a threshold is met once
    """

    def __init__(self, configDict, inputs):
        """!
        Constructor for Instantaneous conditions.
        Does not assign additional params, just calls the super class constructor

        @param configDict Dictionary of attributes that describe the Condition
        @param inputs Dictionary within configDict that deals with the sensors the Condition "watches"
        """
        super().__init__(configDict, inputs)

    def check(self):
        """!
        Checks if Instantaneous condition is fulfilled
        This just returns the result of evaluating the condition string.

        takes no paramters.
        """
        # print('Condition.check()')
        return self.evaluate()

class Duration(Condition):
    """!
    Sub class of Condition that is fulfilled if a threshold is met for a given duration
    """

    def __init__(self, configDict, inputs):
        """!
        Constructor for Duration conditions.
        Assigns Duration-specific attributes:
        duration: the duration for which the threshold condition must be met
        times: a list of times that the condition was true, used for check() method 

        @param configDict Dictionary of attributes that describe the Condition
        @param inputs Dictionary within configDict that deals with the sensors the Condition "watches"
        """
        self.duration = configDict.get('duration')
        self.times = []
        super().__init__(configDict, inputs)
        

    def check(self):
        """!
        Checks if Duration condition is fulfilled
        Uses list of times to figure out whether the threshold condition has been true for the
        designated duration.

        takes no paramters.
        """
        if self.evaluate(): #if condition threshold currently met
            self.times.append(time.time()) 

            #checks if time between first and last occurences of the threshold being met
            #exceeds the minumum duration to activate the control
            if self.times and self.times[-1] - self.times[0] >= self.duration:
                return True

        else: #if condition threshold not met, clears the list
            self.times.clear()
            return False

class Repetition(Condition):
    """!
    Sub class of Condition that is fulfilled if a threshold is met a given number of times in a given duration
    """

    def __init__(self, configDict, inputs):
        """!
        Constructor for Repetition conditions.
        Assigns Repetition-specific attributes:
        duration: the maximum duration within which the repetitions must occur
        reps: the number of repetitions (threshold conditions met) that must occur within the duration
        times: a list of times that the condition was true, used for check() method 

        @param configDict Dictionary of attributes that describe the Condition
        @param inputs Dictionary within configDict that deals with the sensors the Condition "watches"
        """
        self.duration = configDict.get('duration')
        self.reps = configDict.get('reps')
        self.times = []
        super().__init__(configDict, inputs)

    def check(self):
        """!
        Checks if Repetition condition is fulfilled
        Uses list of times to figure out whether the threshold condition has been true for the min
        number of times within a limited time period

        takes no paramters.
        """
        if self.evaluate(): #if condition threshold currently met
            self.times.append(time.time())

            #gets rid of repetitions outside of the max duration
            while self.times and self.times[-1] - self.times[0] > float(self.duration):
                self.times.pop(0)
            #checks if number of remaining occurances exceeds minimum reps to activate control
            if len(self.times) >= int(self.reps):
                return True
        return False


class Action:
    """!
    Super class for Actions that a Control performs. There are 3 subclasses:
    Log (which logs a message to for viewing errors),
    Warning (which sends a warning message and suggestion to the driver dashboard), and 
    Write (which writes to a sensor or other device on the vehicle)
    """

    def __init__(self):
        """!
        Generic template constructor for all Actions.
        Currently this does nothing.

        takes no paramters.
        """
        pass
    
    def execute(self):
        """!
        Generic template execute method for all Actions.
        Performs the Action.
        Currently this does nothing.

        takes no paramters.
        """
        pass
    
    def unexecute(self):
        """!
        Generic template execute method for all Actions.
        Undoes the Action.
        Currently this does nothing.

        takes no paramters.
        """
        #currently this exists just to remove WARNINGS
        pass
    

class Log(Action):
    """!
    Sub class of Action that logs a message to for viewing errors 
    """

    def __init__(self, configDict):
        """!
        Constructor for Log action.
        Assigns Log-specific attributes:
        message: the message to be logged when the Control is triggered

        @param configDict Dictionary of attributes that describe the Action
        """
        self.message = configDict.get('message')

    def execute(self):
        """!
        Executes the Log action by publishing its message to the 'logs' Redis channel

        takes no paramters.
        """
        Redisdata.publish('logs',self.message)
        pass


class Warning(Action):
    """!
    Sub class of Action that a warning message and suggestion to the driver dashboard
    """

    def __init__(self, configDict):
        """!
        Constructor for Warning action.
        Assigns Warning-specific attributes:
        message: the message notifying the driver what is wrong
        suggestion: a suggested action the driver should take to mitigate the problem they're being warned about
        priority: importance of the warning on a scale of 1-10, used to decide which warngins to display on the dashboard

        @param configDict Dictionary of attributes that describe the Action
        """
        self.message = configDict.get('message')
        self.suggestion = configDict.get('suggestion')
        self.priority = configDict.get('priority')

    def execute(self):
        """!
        Executes the Warning action by adding the warning to a local list of warnings,
        sorting this list, and updating the JSON file containing warnings used by dashboard's software.

        takes no paramters.
        """
        # print('Trying to execute WARNING action')
        global warnings
        warningEntry = {'message':self.message, 'suggestion':self.suggestion, 'priority':self.priority}
        #check if warning is already present, add it if it's not
        if warningEntry not in warnings:
            warnings.append(warningEntry)
            #sorts list of warnings by priority, reverse = true means it sorts high to low
            warnings = sorted(warnings, key = lambda i: i['priority'], reverse = True)
            updateJSON()
        
    
    def unexecute(self):
        """!
        Disables the Warning action by removing the warning from a local list of warnings,
        then updating the JSON file containing warnings used by dashboard's software.

        takes no paramters.
        """
        global warnings

        #keep warnings other than the one we want to remove
        warnings = [i for i in warnings if not (i['message'] == self.message)] 
        #no need to sort here because deleting an item will not affect the order of the rest
        
        updateJSON()

class Write(Action):
    """!
    Sub class of Action that writes to a sensor or other device on the vehicle
    """

    def __init__(self, configDict):
        """!
        Constructor for Write action.
        Assigns Write-specific attributes:
        sensor: the name of the sensor/device to write to
        value: the value to write to this sensor

        @param configDict Dictionary of attributes that describe the Action
        """
        self.sensor = configDict.get('sensor')
        self.value = configDict.get('value')

    def execute(self):
        """!
        Executes the Write action by invoking the driver to write to this sensor.

        takes no paramters.
        """
        # print('Trying to execute WRITE action')
        driver.write(self.sensor, self.value)

def updateJSON():
    """!
    Helper method for Warning actions, generates a dictionary structure compatible with dashboard's software
    and writes the updated dictionary to dashboard's JSON file

    takes no paramters.
    """

    dashboardDict =  { 'sensor_readings': sensorReadings, 'warnings': warnings }
    # print('DASHBOARD DICT BEFORE JSON WRITE')
    # print(dashboardDict)
    with open('/usr/etc/dashboard.json','w') as outfile:
        # outfile.write(json.dumps(dashboardDict))
        json.dump(dashboardDict, outfile)


def watch(message):
    """!
    This is the method that runs whenever new data is received in Redis. Extracts data from the Redis message, 
    checks if it is relevant to the dashboard and updates the JSON file if it is,
    checks if it is relevant to a Control defined in config and updates the Control if it is

    takes no paramters.
    """
    #get data from Redis
    split_key = message.split(':',1)
    sensor = split_key[0]
    val = split_key[1]
    #update local data stroage vector
    DataStorage[sensor] = val

    #updates JSON if the sensor is displayed on the dashboard
    if sensor in dashboardSensors and sensorReadings[sensor] != val:
        sensorReadings[sensor] = val
        updateJSON()

    #updates Control objects relevant to the sensor, if any
    relevantControls = ControlsDict[sensor]
    if relevantControls is not None:
        for control in relevantControls:
            # print ('updating control ' + str(control))
            control.update()


#SETUP PROCEDURE

#Setting up connection to Redis Server
Redisdata = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
data = Redisdata.pubsub()
data.subscribe('calculated_data')

allControls = config.get('Controls') #complete list of sensor configurations to make objects from
ControlsDict = defaultdict(list) #dictionary of (lists of) controls organized by the input sensor (key = sensor name)
DataStorage = {} #dictionary of current values of every sensor
# defaultControlDict = ControlsList.get('default_control')

#create dashboard data objects, fill sensorReadings for the dashboard with preliminary data
warnings = []
sensorReadings = {}
dashboardSensors = config.get('EPAL').get('display_sensors')
for sensorName in dashboardSensors:
    sensorReadings[sensorName] = -1.0
dashboardDict =  { 'sensor_readings': sensorReadings, 'warnings': warnings }
updateJSON()

#Control object instantiation procedure
for controlString in allControls:
    configDict = allControls.get(controlString)
    #constructs the control
    control = Control(configDict)
    inputs = configDict.get('inputs').values()
    for i in inputs:
        ControlsDict[i].append(control) #stores controls under the sensor inputs they use
        #this is done because the Watcher looks for controls relevant to incoming data inputs


#ACTUAL CODE THAT RUNS
while True:
    #polls for new data from Redis
    message = data.get_message()
    if (message and (message['data'] != 1 )):
        if message['channel'] == 'calculated_data':
            watch(message['data'])
    time.sleep(.01)
