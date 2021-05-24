#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Mithil Shah,Irwin Frimpong,Harrison Walker,Lia Chrysanthopoulos, Adam Tunnell                                    
## Last Updated : 05/23/2021                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: emulated_driver.py                                                 
## Description: Driver for interfacing with emulated snensor
## contains methods to create emulated sensor objects and read/write from them
#############################################################################################

import math
import time
import sys
import os

# Importing the config file
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config

class SensorEmulator():
    """!
    Super class for all sensor emulator objects. There are 3 subclasses:
    ConstantEmulator, SineEmulator, and RampEmulator
    """

    def __init__(self, configDict):
        """!
        Generic constructor method used for all sensor emulators.
        Assigns attributes that all types of emulators use: 
        period (repeating period of data pattern)
        values (range of data values the emulator produces)

        Also assigns the start time of the current period to the current time

        @param configDict Dictionary of sensor attributes that describe the emulated sensor
        """
        self.period = configDict.get('data_period')
        self.periodStart = time.time()
        self.values = configDict.get('data_values')

    def getValue(self):
        """!
        Generic method to retrieve a value from sensor emulators.
        Calculates time elapsed into current data period and calls the pattern-specific calculateValue
        to assign a new current value

        takes no parameters.
        """
        # calculate time into period
        timeElapsed = time.time()-self.periodStart
        # check to see if in new period
        if type(self) is not ConstantEmulator:
            while timeElapsed > self.period:
                # reset periodStart and timeElapsed for new period
                self.periodStart = time.time()
                timeElapsed = timeElapsed - self.period
        self.currValue = self.calculateValue(timeElapsed)
        # print('about to return a current value of ' + str(self.currValue))
        return self.currValue

    def calculateValue(self, timeElapsed):
        """!
        Generic method to calculate value of sensor based on its data pattern.
        This method returns Null, is only used if an invalid data-pattern is defined in config.

        @param timeElapsed the time elapsed into the current data period
        """
        return None


class ConstantEmulator(SensorEmulator):
    """!
    Sub class of SensorEmulator that returns a constant value
    """

    def __init__(self, configDict):
        """!
        Constructor for ConstantEmulator.
        Sets the current value to the constant value defined in config

        @param configDict Dictionary of sensor attributes that describe the emulated sensor
        """
        super().__init__(configDict)
        self.currValue = self.values

    def getValue(self):
        """!
        Override method to retrieve a value from ConstantEmulator.
        Just returns the current value instead of calculating a value from config.
        Note that ConstantEmulators do not have a calculateValue method
        """
        return self.currValue
        # done this way instead of deriving a value based on config like other data patterns
        # so that a different constant value can be written to the sensor


class SineEmulator(SensorEmulator):
    """!
    Sub class of SensorEmulator that returns values along a sine wave
    """
    
    def __init__(self, configDict):
        """!
        Constructor for SineEmulator.
        Assigns attributes used only for sine waves: 
        avg: "center line" average sine wave value
        mag: magnitude of sine wave

        @param configDict Dictionary of sensor attributes that describe the emulated sensor
        """
        super().__init__(configDict)
        self.avg = (self.values[0] + self.values[1]) / 2
        self.mag = abs(self.values[1] - self.values[0]) / 2

    def calculateValue(self, timeElapsed):
        """!
        Calculates value for a sine wave using math library function.

        @param timeElapsed the time elapsed into the current data period
        """
        return self.avg + self.mag * math.sin(2 * math.pi / self.period * timeElapsed)


class RampEmulator(SensorEmulator):
    """!
    Sub class of SensorEmulator that returns values along a ramp (triangle wave)
    """

    def __init__(self, configDict):
        """!
        Constructor for RampEmulator.
        Assigns attribute used only for ramps: 
        slope: the slope of the ramp during the first half of the data period
        (the opposite slope is used for the second half)

        @param configDict Dictionary of sensor attributes that describe the emulated sensor
        """
        super().__init__(configDict)
        self.slope = 2 * (self.values[1] - self.values[0])/self.period

    def calculateValue(self, timeElapsed):
        """!
        Calculates value for a ramp/triangle wave.

        @param timeElapsed the time elapsed into the current data period
        """
        # second half of period going down
        if timeElapsed > 0.5 * self.period:
            return self.values[1] - self.slope*(timeElapsed - self.period/2)
        # first half of period going up
        return self.values[0] + self.slope*timeElapsed


class CycleEmulator(SensorEmulator):
    """!
    Sub class of SensorEmulator that return values based on a cycle of constant values.
    (especially useful for emulating states)
    Each value in this cyle is given equal time.
    """

    def __init__(self, configDict):
        """!
        Constructor for ConstantEmulator.
        Does not assign additional attributes, just calls the super class constructor

        @param configDict Dictionary of sensor attributes that describe the emulated sensor
        """
        super().__init__(configDict)

    def calculateValue(self, timeElapsed):
        """!
        Returns a value within a list of cycling values.
        Does so by getting item within list based on temporal position in data period
        e.g. if you are halfway through the data period, it will return value halfway through list

        @param timeElapsed the time elapsed into the current data period
        """
        index = int( math.floor( (timeElapsed/self.period)*len(self.values) ) )
        return self.values[index]


def read(sensorName):
    """!
    reads value from emulated sensor by calling getValue method on the corresponding
    element of the list that holds all emulators.
    

    @param sensorName The name of the sensor to be read
    """
    return emulators[sensorName].getValue()


def write(sensorName, value):
    """!
    Writes emulated sensor by setting its currValue to the given values.
    This method exists to comply with universal format of all other drivers.
    Note: You will not see the results of this method unless using a constant emulator
    because they return to their original data pattern the next time you read this

    @param sensorName The name of the sensor to be written to
    @param value The value to write to this sensor.
    """
    print('About to write to ' + sensorName + ', ' + str(value))
    emulators[sensorName].currValue = value
    print(emulators[sensorName].currValue)


def configure_emulator(sensorDict):
    """!
    Uses the subclass constructor methods defined in this file to set up emulator objects.
    Checks data_pattern from config and calls the corresponding constructor.

    @param sensorDict Dictionary of sensor attributes that describe the emulated sensor
    """
    pattern = sensorDict.get('data_pattern')
    if pattern == 'CYCLE':
        return CycleEmulator(sensorDict)
    elif pattern == 'SINE':
        return SineEmulator(sensorDict)
    elif pattern == 'RAMP':
        return RampEmulator(sensorDict)
    elif pattern == 'CONSTANT':
        return ConstantEmulator(sensorDict)
    else:
        print('sensor called' +
              sensorDict['var_name'] + 'could not be configured')
        return None


#This is the actual procedure that runs

allSensors = config.get('Sensors')
emulators = {}  # holds all the emulated sensor objects

#goes through all sensors in config
for sensorName in allSensors:
    sensorDict = allSensors.get(sensorName)
    #if sensor is an emulator, it initializes/configures it
    if sensorDict['bus_type'] == 'EMULATED':
        emulators[sensorName] = (configure_emulator(sensorDict))
