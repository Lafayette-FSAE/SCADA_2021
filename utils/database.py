##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker,Lia Chrysanthopoulos, Mithil Shah, Adam Tunnell, Irwin Frimpong                                   
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: database.py                                                 
## Description: Database module holds methods to retrieve sensor data from local Postgresql Database                    
#############################################################################################

import sys
import os
import datetime
import time
import psycopg2

#set up database connection. These are agreed upon parameters, and can be changed as needed
#as long as the Postgres database is created accordingly with the same parameters
database = psycopg2.connect(
    user='pi',
    password='scada',
    host='localhost',
    port='5432',
    database='test'
)

cursor = database.cursor()

def getData(sensor_id):
    """
        For a sensor name, return the last value of the data associated with it,
        if it exists. To be used by other classes to retreive information
        from database. Note: this used to be used to fill the data display GUI,
        but we've since found a more efficient way to do that. I don't think it's
        being used anymore
    """
    cursor.execute("""
        SELECT value
        FROM data
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """, [sensor_id])

    data = cursor.fetchall()
    if len(data)==0:
        #If this is the case then there is an issue somewhere in the data path driver->sorter->calibrator->logger->database
        #or nothing (not even 'no data') has been added to the database for a sensor
        return 'ERR IN DATAPATH'
        
    return data[0][0]

def getAllData(sensor_id):
    """
        For a sensor name, returns all data associated with it,
        if it exists. To be used by other classes to retreive information
        from database.
    """
    #print(sensor_id)
    cursor.execute(""" 
        SELECT value, timestamp
        FROM data
        WHERE sensor_id = %s
        ORDER BY timestamp ASC
    """, [sensor_id])

    data = cursor.fetchall()
    if len(data)==0:
        #If this is the case then there is an issue somewhere in the data path driver->sorter->calibrator->logger->database
        #or nothing (not even 'no data') has been added to the database for a sensor
        return 'ERR IN DATAPATH'
        
    return data

def getAllLogs():
    """
        Return all log data. To be used by other classes to retreive information
        from database.
    """
    #print(sensor_id)
    cursor.execute(""" 
        SELECT message, timestamp
        FROM logs
        ORDER BY timestamp ASC
    """)

    data = cursor.fetchall()
    # if data == None or len(data) == 0:
    if len(data)==0:
        #If this is the case then there are not yet logs from Watcher in the database
        return 'NO LOGS'
        
    return data

def getAllDataWithinPeriod(sensor_id, timeStampBegin, timeStampEnd):
    """
        For a sensor name, returns all data associated with it within a desired time period,
        if it exists. To be used by other classes to retreive information
        from database. This is really just a prototype for a similar method in Postman.
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
        #If this is the case then there is an issue somewhere in the data path driver->sorter->calibrator->logger->database
        #or nothing (not even 'no data') has been added to the database for a sensor
        return 'ERR IN DATAPATH'
        
    return data 