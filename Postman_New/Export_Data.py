#!/usr/bin/python3

import sys, os

lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
lib_path = os.path.join(lib_path, 'utils')

sys.path.append(lib_path)
sys.path.append(config_path)


import psycopg2
import openpyxl
import config
import pandas as pd
import Extract_Data
import matplotlib.pyplot as plt
import numpy as np


def export(sensorNames, sensorData, timestampBegin, timestampEnd, samplePeriodDes, filePath='./defaultFileName'):
    '''
    main method of Export_Data module

    takes in 
    - sensorNames: a list [] of the sensors to be exported and
    - sensorData: a list of lists [[sensor1Data],[sensor2Data],[sensor3Data]] of all data falling between the given timestamps
    - timeStampBegin: timestamp of session start
    - timeStampEnd: timestamp of session end
    - samplePeriodDes: desired sample Period of the outputted data
    - filePath: path/name of Excel file to save exported data to

    executes procedure
    - calls processData
    - genePeriod timestamp array for y axis label
    - open new Excel Workbook and Sheet to write to
    - place header (x axis label) row with sensor id's
    - uses a loop structure to place data in Excel sheet
    - save notebook

    no return value
    '''

    #####################################
    # doing Excel stuff with fake data

    dummyNames = ['a', 'b', 'c', 'd', 'e']
    dummyList = [[] for _ in range(5)]

    for i in range(5):
        for j in range(5):
            dummyList[i].append(str(10*i + j))

    processedData = dummyList
    print ('dummyList: ' + str(dummyList))
    sensorNames = dummyNames
    #####################################

    # processedData = processData(sensorData)

    #TODO: Here we will genePeriod an array of timestamps based on timeStampBegin, timeStampEnd, and sample Period
    # and insert it in processedData as the first list i.e. first column in the Excel workbook

    wb = openpyxl.Workbook()
    ws = wb.active

    # build headers list
    headers = sensorNames
    # insert time heading on left side of row
    headers.insert(0, 'Timestamp')
    #add headers to Excel sheet
    ws.append(headers)

    print("zipped: " + str(zip(processedData)))

    #add real data to Excel sheet
    for row in zip(processedData):
        print('row:' + str(row))
        ws.append(row)

    wb.save(filePath)


def processData(sensorNames, sensorData, timeStampBegin, timeStampEnd, samplePeriodDes):
    '''
    takes in 
    - sensorNames: a list [] of the sensors to be exported and
    - sensorData: a list of lists [[sensor1Data],[sensor2Data],[sensor3Data]] of all data falling between the given timestamps
    - timeStampBegin: timestamp of session start
    - timeStampEnd: timestamp of session end
    - samplePeriodDes: desired sample Period of the outputted data

    executes procedure
    - calls getSamplePeriods
    - find data lower frequency than samplePeriodDes and interpolate it
    - find data higher frequency than samplePeriodDes and decimate it
    - after modifying each data set, put it into a corresponding list in the processedData data structure



    returns processedData: a list of lists [[sensor1Data],[sensor2Data],[sensor3Data]] of all data falling between the given timestamps,
                            but processed


    '''
    samplePeriods, displayVariables = getSensorInfo(sensorNames)
    samplePeriodDesMS = samplePeriodDes * 1000
    sharedIndex = pd.date_range(start = timeStampBegin, end = timeStampEnd, freq = ('%ims' % samplePeriodDesMS)).to_series()
    # genePeriods empty list of lists to store new (processed) data in
    processedData = [[] for _ in range(len(sensorNames))]

    for sensorIdx in range(len(sensorData)):
        currSamplePeriod = samplePeriods[sensorIdx]
        currDisplayVariable = displayVariables[sensorIdx]
        data, index = zip(*sensorData[sensorIdx])

        if(currDisplayVariable == 'state'):
            data = pd.Series(data = data, index = index)

            data = shiftData(data, sharedIndex, currSamplePeriod)
            # print("shifted:\n %s\n" % data)
            processedData = undifferentiateData(data, currSamplePeriod)
        else:
            data = pd.Series(data = map(float,data), index = index)
            # print("sample period: %s\n" % currSamplePeriod)

            # print("data:\n %s\n" % data)
            data = shiftData(data, sharedIndex, currSamplePeriod)
            # print("shifted:\n %s\n" % data)
            data = undifferentiateData(data, currSamplePeriod)
            # print("undifferentiated:\n %s\n" % data)
            processedData[sensorIdx] = interpolateData(data, samplePeriodDes)


    return processedData


def getSensorInfo(sensorNames):
    Periods = []
    displayVariables = []
    for sensor in sensorNames:
        Periods.append(config.get('Sensors').get(sensor).get('sample_period'))
        displayVariables.append(config.get('Sensors').get(sensor).get('display_variable'))

    return Periods, displayVariables



def interpolateData(data, samplePeriodDes):

    return data.resample('%ims' % ((samplePeriodDes * 1000)/100), origin = 'start').mean().interpolate()  

def shiftData(data, index, sensorSamplePeriod):
    oldIndex = pd.date_range(start = index.index[0], end = index.index[-1], freq = ('%ims' % (sensorSamplePeriod * 1000))).to_series()
    data = data.reindex_like(oldIndex, method = 'ffill')
    # print("Reindexed to Current Index:\n %s\n" % data)
    return data.reindex_like(index)

def undifferentiateData(data, sensorSamplePeriod):
    outputData = data.resample('%ims' % (sensorSamplePeriod * 1000), origin = 'start').ffill()
    outputData[-1] = data[-1]
    return outputData

# THIS IS THE PROCEDURE TO BE CALLED FROM THE GUI
# ip_address = config.get("Post_Processing").get("ip_address")
# ip_address = '139.147.81.105'
ip_address = '139.147.91.187'
ex_sum_sensors = config.get("Post_Processing").get("expensive_summary_data")
## get cheap summary data 
Extract_Data.initialize_database(ip_address)
Extract_Data.getDelimiter()
timeData = Extract_Data.getTimeStamps()
timeStamps = timeData[0]
durations = timeData[1]

thisSessionStamps = timeStamps[-2]
relevantData = Extract_Data.getSensorData("emulator_tsi_drive_state", thisSessionStamps[0], thisSessionStamps[1])
# print('data for ' + ex_sum_sensors[0] + ' follows')
print(str(relevantData))

sensorNames = []
sensorNames.append(ex_sum_sensors[0])
sensorData = []
sensorData.append(relevantData)
timestampBegin = thisSessionStamps[0]
timestampEnd = thisSessionStamps[1]
# export(sensorNames=None, sensorData=None, timestampBegin=None, timestampEnd=None, samplePeriodDes=1, filePath='./defaultFileName'

# print(sensorData[0])
# print(sensorData[0])

print('tsb: %s\n tse %s' % (timestampBegin, timestampEnd))

data = processData(['emulator_tsi_drive_state'], [sensorData[0]], timestampBegin, timestampEnd, .5)
print("output: \n%s\n" % data)
# data[0].plot(style = 'ok')
# inputdata, inputindex = zip(*sensorData[0])
# pd.Series(data = map(float,inputdata), index = inputindex).plot(style = 'ob')
# plt.legend(['output','input'], loc = 'upper left')
# plt.show()
# sharedIndex = pd.date_range(start = timestampBegin, end = timestampEnd, freq = ('%ims' % 1000)).to_series()
# data = interpolateData(sensorData[0], sharedIndex,.5, 1)
# print("last val: %s" % data[-1])
# print("unshifted: ")
# print(data)
# print('\n')
# data = shiftData(data)
# print("shifted: ")
# print(data)
# print('\n')