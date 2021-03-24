import sys
import os
import datetime
import time
import psycopg2


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
        from database.
    """
    #print(sensor_id)
    cursor.execute("""
        SELECT value
        FROM data
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """, [sensor_id])

    data = cursor.fetchall()
    # if data == None or len(data) == 0:
    if len(data)==0:
        #If this is the case then there is an issue with the logger class' update method
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
    # if data == None or len(data) == 0:
    if len(data)==0:
        #If this is the case then there is an issue with the logger class' update method
        return 'ERR IN DATAPATH'
        
    return data

def getAllDataWithinPeriod(sensor_id, timeStampBegin, timeStampEnd):
    """
        For a sensor name, returns all data associated with it within a desired time period,
        if it exists. To be used by other classes to retreive information
        from database.
    """
    #print(sensor_id)
    cursor.execute("""
        SELECT value, timestamp
        FROM data
        WHERE sensor_id = %s && timestamp>= %s && timestamp <= %s
        ORDER BY timestamp ASC
    """, [sensor_id, timeStampBegin, timeStampEnd])

    data = cursor.fetchall()
    # if data == None or len(data) == 0:
    if len(data)==0:
        #If this is the case then there is an issue with the logger class' update method
        return 'ERR IN DATAPATH'
        
    return data