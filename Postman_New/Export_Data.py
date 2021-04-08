#!/usr/bin/python3

import sys, os

lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
lib_path = os.path.join(lib_path, 'utils')

sys.path.append(lib_path)
sys.path.append(config_path)


from utils import database
import psycopg2
import openpyxl
import config
import pandas as pd


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
    samplePeriods = getSamplePeriods(sensorNames)

    # genePeriods empty list of lists to store new (processed) data in
    processedData = [[] for _ in range(len(sensorNames))]

    for sensorIdx in sensorData:
        currSamplePeriod = samplePeriods[sensorIdx]

        if currSamplePeriod > samplePeriodDes:
            processedData[sensorIdx] = interpolateData(
                sensorData[sensorIdx], samplePeriodDes, currSamplePeriod)
        elif currSamplePeriod < samplePeriodDes:
            processedData[sensorIdx] = decimateData(
                sensorData[sensorIdx], samplePeriodDes, currSamplePeriod)
        else:
            processedData[sensorIdx] = shiftData(sensorData[sensorIdx])

    return processedData


def getSamplePeriods(sensorNames):
    '''
    this needs to use postgres to retrieve the samplePeriods

    '''
    Periods = []
    return Periods


def interpolateData(data, samplePeriodDes):
    '''

    '''
    samplePeriodDesMS = samplePeriodDes * 1000
    outputData = pd.Series(database.getData(data)).resample('%i%s' % (samplePeriodDesMS/100,'ms')).interpolate().asfreq('%i%s' % (samplePeriodDesMS,'ms'))
    return outputData


def decimateData(data, samplePeriodDes):
    '''

    '''
    samplePeriodDesMS = samplePeriodDes * 1000
    outputData = pd.Series(database.getData(data)).resample('%i%s' % (samplePeriodDesMS,'ms')).interpolate()
    return outputData

def shiftData(data):
    '''
    ''' 

    outputData = []
    return outputData

# THIS IS THE PROCEDURE TO BE CALLED FROM THE GUI
# ip_address = config.get("Post_Processing").get("ip_address")
ip_address = '139.147.91.184'
ex_sum_sensors = config.get("Post_Processing").get("expensive_summary_data")
## get cheap summary data 
Extract_Data.initialize_database(ip_address)
Extract_Data.getDelimiter()
timeData = Extract_Data.getTimeStamps()
timeStamps = timeData[0]
durations = timeData[1]

thisSessionStamps = timeStamps[0]
relevantData = Extract_Data.getSensorData(ex_sum_sensors[0], thisSessionStamps[0], thisSessionStamps[1])
print('data for ' + ex_sum_sensors[0] + ' follows')
print(str(relevantData))

sensorNames = []
sensorNames.append(ex_sum_sensors[0])
sensorData = []
sensorData.append(relevantData)
timestampBegin = thisSesssionStamps[0]
timestampEnd = thisSesssionStamps[1]
# export(sensorNames=None, sensorData=None, timestampBegin=None, timestampEnd=None, samplePeriodDes=1, filePath='./defaultFileName'

