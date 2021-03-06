#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: Exporrt_Data.py                                                 
## Description: Class that contains methods to retrieve data from the database for Post Processing.              
#############################################################################################


import sys, os

lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
lib_path2 = os.path.join(lib_path, 'utils')

sys.path.append(lib_path)
sys.path.append(lib_path2)
sys.path.append(config_path)


import psycopg2
import openpyxl
import config
import pandas as pd
import Extract_Data


def export(sensorNames, sensorData, timestampBegin, timestampEnd, samplePeriodDes, filePath):
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
    - generate timestamp array for y axis label
    - open new Excel Workbook and Sheet to write to
    - place header (x axis label) row with sensor id's
    - uses a loop structure to place data in Excel sheet
    - save notebook

    no return value
    '''
    #####################################
    #real data procedure 

    processedData = processData(sensorNames, sensorData, timestampBegin, timestampEnd, samplePeriodDes)

    #TODO: Here we will generate an array of timestamps based on timeStampBegin, timeStampEnd, and sample Period
    # and insert it in processedData as the first list i.e. first column in the Excel workbook

    #####################################
    # doing Excel stuff with fake data

    # dummyNames = ['a', 'b', 'c', 'd', 'e']
    # dummyList = [[] for _ in range(6)]
    # dummyList[0] = [0.0, 0.1, 0.2, 0.3, 0.4]
    # for i in range(5):
    #     for j in range(5):
    #         dummyList[i+1].append(str(10*i + j))

    # processedData = dummyList
    # print ('dummyList: ' + str(dummyList))
    # sensorNames = dummyNames

    wb = openpyxl.Workbook()
    ws = wb.active

    # build headers list
    headers = sensorNames
    # insert time heading on left side of row
    headers.insert(0, 'Timestamp')
    #add headers to Excel sheet
    ws.append(headers)

    #add real data to Excel sheet
    for row in zip(*processedData):
        print('row:' + str(row))
        ws.append(row)

    # x_data = openpyxl.chart.Reference(ws, min_col=1, min_row=2, max_row=len(processedData[0])+1)
    # print('x_data:')
    # print(x_data)
    # chart = openpyxl.chart.LineChart()
    # for i in range(len(dummyList)-1):
    #     y_data = openpyxl.chart.Reference(ws, min_col=i+2, min_row=2, max_row=len(processedData[0])+1)
    #     title = openpyxl.
    #     print('y_data:')
    #     print(y_data)
    #     s = openpyxl.chart.Series(y_data, xvalues = x_data)
    #     # print(s)
    #     chart.append(s)
    # sensorNames = openpyxl.chart.Reference(ws, min_col=2, min_row=2, max_row=len(processedData))
    # chart.set_categories(sensorNames)    

    # # values = openpyxl.chart.Reference(ws, min_col=1, min_row=1, max_col=6, max_row=6)
    # # chart = openpyxl.chart.LineChart()
    # # chart.add_data(values, titles_from_data=True)
    
    
    # ws.add_chart(chart, "E15")

    filePath = filePath + '.xlsx'
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
    - creates a common index to be shared by all sensors and makes it the first element in the processedData list
    - calls getSensorInfo to get sample periods and display variables
    - shifts data onto a common index using shiftData
    - undifferentiates data
    - if the display variable isn't a state, interpolates data
    - converts data to list and appends it onto processedData list



    returns processedData: a list of lists [[newTimeVector],[sensor1Data],[sensor2Data],[sensor3Data]] of all data falling between the given timestamps,
                            but processed and aligned to a single time vector stored in the first list


    '''

    #get sample periods and display variables of each sensor
    samplePeriods, displayVariables = getSensorInfo(sensorNames)

    #create an index to be shared by all sensor data
    sharedIndex = pd.date_range(start = timeStampBegin, end = timeStampEnd, freq = ('%fms' % (samplePeriodDes * 1000)))
    sharedIndex = sharedIndex.to_series()

    # generates empty list of lists to store new (processed) data in
    processedData = [[] for _ in range(len(sensorNames))]
    processedData[0] = sharedIndex.tolist()

    for sensorIdx in range(len(sensorData)):
        currSamplePeriod = samplePeriods[sensorIdx]
        currDisplayVariable = displayVariables[sensorIdx]

        #unzip sensor data
        data, index = zip(*sensorData[sensorIdx])

        #state sensors are not interpolated and their data is kept as a string
        if(currDisplayVariable == 'state'):
            data = pd.Series(data = data, index = index)

            data = shiftData(data, sharedIndex, currSamplePeriod)

            data = undifferentiateData(data, currSamplePeriod)
        else:
            data = pd.Series(data = map(float,data), index = index)

            data = shiftData(data, sharedIndex, currSamplePeriod) 

            data = undifferentiateData(data, currSamplePeriod)

            data = interpolateData(data, samplePeriodDes)

        processedData.append(data.tolist())

    return processedData


#returns lists of sample periods and display variables when given a list of sensor names
def getSensorInfo(sensorNames):
    Periods = []
    displayVariables = []
    for sensor in sensorNames:
        Periods.append(config.get('Sensors').get(sensor).get('sample_period'))
        displayVariables.append(config.get('Sensors').get(sensor).get('display_variable'))

    return Periods, displayVariables


#interpolates data at a frequency 100 times higher than desired and then converts back to the desired frequency
def interpolateData(data, samplePeriodDes):

    return data.resample('%fms' % ((samplePeriodDes * 1000)/100), origin = 'start').mean().interpolate().asfreq('%fms' % ((samplePeriodDes * 1000)))

#converts index of data to what it ideally should have been and forward fills and then converts to the desired index without filling empty slots
def shiftData(data, index, sensorSamplePeriod):
    oldIndex = pd.date_range(start = index.index[0], end = index.index[-1], freq = ('%fms' % (sensorSamplePeriod * 1000))).to_series()
    outputData = data.reindex_like(oldIndex, method = 'ffill')
    #forward fill doesn't always keep the last value so the last value is manually inserted
    outputData[-1] = data[-1]
    return outputData.reindex_like(index)

#resamples at the data at the sample period and forward fills the empy slots
def undifferentiateData(data, sensorSamplePeriod):
    outputData = data.resample('%fms' % (sensorSamplePeriod * 1000), origin = 'start').ffill()
    #forward fill doesn't always keep the last value so the last value is manually inserted
    outputData[-1] = data[-1]
    return outputData

# THIS IS THE PROCEDURE TO BE CALLED FROM THE GUI
ip_address = config.get("Post_Processing").get("ip_address")
# ip_address = '139.147.81.105'
#ip_address = '139.147.91.189'

ex_sum_sensors = config.get("Post_Processing").get("expensive_summary_data")
## get cheap summary data 
Extract_Data.initialize_database(ip_address)
Extract_Data.getDelimiter()
timeData = Extract_Data.getTimeStamps()
timeStamps = timeData[0]
durations = timeData[1]

sensorTesting = "emulator_car_mph"

thisSessionStamps = timeStamps[50]
relevantData = Extract_Data.getSensorData(sensorTesting, thisSessionStamps[0], thisSessionStamps[1])
print('data for '+ sensorTesting +' follows')
print(str(relevantData))

sensorNames = []
sensorNames.append(sensorTesting)
sensorData = []
sensorData.append(relevantData)
timestampBegin = thisSessionStamps[0]
timestampEnd = thisSessionStamps[1]
# export(sensorNames=None, sensorData=None, timestampBegin=None, timestampEnd=None, samplePeriodDes=1, filePath='./defaultFileName'

# print(sensorData[0])
# print(sensorData[0])

print('tsb: %s\n tse %s' % (timestampBegin, timestampEnd))

data = processData([sensorTesting], [sensorData[0]], timestampBegin, timestampEnd, .5)
print("output: \n%s\n" % data)

# data[0].plot(style = 'ok')
# inputdata, inputindex = zip(*sensorData[0])
# pd.Series(data = map(float,inputdata), index = inputindex).plot(style = 'ob')
# plt.legend(['output','input'], loc = 'upper left')
# plt.show()
# sharedIndex = pd.date_range(start = timestampBegin, end = timestampEnd, freq = ('%fms' % 1000)).to_series()
# data = interpolateData(sensorData[0], sharedIndex,.5, 1)
# print("last val: %s" % data[-1])
# print("unshifted: ")
# print(data)
# print('\n')
# data = shiftData(data)
# print("shifted: ")
# print(data)
# print('\n')

#TESTING FOR EXPORT TO EXCEL PART
# print('About to test Excel Export:')
# export([sensorTesting], [sensorData[0]], timestampBegin, timestampEnd, .5)