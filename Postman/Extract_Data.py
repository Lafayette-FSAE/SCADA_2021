#!/usr/bin/python3
import sys
import os
import psycopg2
import statistics

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: Extract_Data.py                                                 
## Description: This class gets the data for the specified session in Postgres.              
#############################################################################################

# config_path = os.getcwd() + '/config'
# sys.path.append(config_path)
# print("__file__ is ")
# #os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))
# print(os.path.join(__file__, '..'))



lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
lib_path = os.path.join(lib_path, 'utils')

sys.path.append(lib_path)
sys.path.append(config_path)

import config

def initialize_database(ip_address): 
    global database
    global timeStampList
    global cursor
    
    database = psycopg2.connect(
        user='pi',
        password='scada',
        host=ip_address,
        port='5432',
        database='test'
    )

    timeStampList = []
    cursor = database.cursor()

## Method gets all sessions and their durations 
def getTimeStamps():

    """
        Return the timestamps
    """

    global delimitSensor

    cursor.execute("""
        SELECT value, timestamp
        FROM data
        WHERE sensor_id = %s
        ORDER BY timestamp ASC
    """, [delimitSensor])

    data = cursor.fetchall()



    if type(data) is str and data == 'ERR IN DATAPATH':
        raise Exception('NO DELIMIT DATA FOUND IN POSTGRES')
    # local variables for time stamps 
    status = False
    begin_time = 0 
    end_time = 0
    timeStampList = [] # list of time stamps 
    durationList = []
    
    
    for row in data:

        # car just started session
        if(evaluate_in_session(row[0]) and status == False):
            status = True
            begin_time = row[1]

        # Car just ended session
        elif(not evaluate_in_session(row[0]) and status == True):
            status = False
            end_time = row[1]
            time = end_time - begin_time
            timeStampList.append([begin_time, end_time])
            durationList.append(time)


    # Catches the end of the last session if system breaks during session
    if status == True:
        end_time = row[1]
        time = end_time - begin_time
        timeStampList.append([begin_time, end_time])
        durationList.append(time)

    #NOTE: WE ARE NOT ACCOUNTING FOR SESSIONS BEING "TRUE" WHEN SYSTEM TURNS OF AND "TRUE" WHEN TURNED BACK ON

    return [timeStampList, durationList]



def getDelimiter():
    global delimitSensor
    global in_session_condition

    delimitInfo = config.get('Post_Processing').get('session_delimiting')
    in_session_condition = delimitInfo.get('in_session_condition')
    delimitSensor = delimitInfo.get('input')
    in_session_condition = in_session_condition.replace('input', delimitSensor.replace('\n',''))
    

def evaluate_in_session(data):
    global delimitSensor
    global in_session_condition
    try:
        if data == 'no data': #will not trigger anything unless there is data for all inputs
            return False
        elif not data.isdecimal(): #for string variables i.e. states
            data = '"' + data + '"' 
        condition = in_session_condition.replace(delimitSensor, data.replace('\n',''))
        return eval(condition)
    except KeyError:
        return False


def getSensorData(sensor_id, timeStampBegin, timeStampEnd):
    """
        For a sensor name, returns all data associated with it within a desired time period,
        if it exists. To be used by other classes to retreive information
        from database.
    """
    #print(sensor_id)
    cursor.execute("""
        SELECT value, timestamp
        FROM data
        WHERE sensor_id = %s and timestamp between %s and %s
        ORDER BY timestamp ASC
    """, [sensor_id, timeStampBegin, timeStampEnd])

    data = cursor.fetchall()
    # if data == None or len(data) == 0:
    if len(data)==0:
        #If this is the case then there is an issue with the logger class' update method
        return 'ERR IN DATAPATH'
        
    return data

def getMean(dataValues):
    return statistics.mean(dataValues)

def getMax(dataValues):
    return max(dataValues)

def getMin(dataValues):
    return min(dataValues)



