
import sys
import os
import psycopg2
config_path = os.getcwd() + '/config'
sys.path.append(config_path)
print("__file__ is ")
#os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))
print(os.path.join(__file__, '..'))

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
    #print("data " + str(data))
    if len(data)==0:
        #If this is the case then there is an issue with the logger class' update method
        return 'NO DATA FOUND FOR POSTGRES'

    # local variables for time stamps 
    status = False
    begin_time = 0 
    end_time = 0
    timeStampList = [] # list of time stamps 
    durationList = []
    
    
    for row in data:

        # Car just started session
        # if(row[0] == start_delim and status == False):
        #     status = True
        #     begin_time = row[1]
        #     #print("Begin ")
        if(evaluate_in_session(row[0]) and status == False):
            status = True
            begin_time = row[1]
            #print("Begin ")

        # Car just ended session
        elif(not evaluate_in_session(row[0]) and status == True):
            status = False
            end_time = row[1]
            time = end_time - begin_time
            timeStampList.append([begin_time, end_time])
            durationList.append(time)

        print('status is' + str(status))

    # Catches the end of the last session if system breaks during session
    if status == True:
        end_time = row[1]
        time = end_time - begin_time
        timeStampList.append([begin_time, end_time])
        durationList.append(time)

    #NOTE: WE ARE NOT ACCOUNTING FOR SESSIONS BEING "TRUE" WHEN SYSTEM TURNS OF AND "TRUE" WHEN TURNED BACK ON


    for i in range(len(timeStampList)):
        print (str(timeStampList[i][0]) +  ' until ' + str(timeStampList[i][1]) + ' duration: ' + str(durationList[i]))

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
        print( 'about to evaluate ' + condition)
        print('evaluated: ' + str(eval(condition)))
        return eval(condition)
    except KeyError:
        return False


def getSensorData(sensor_id, data):
    pass
    # cursor.execute("""
    #     SELECT * from data
    #     WHERE sensor_id = %s
    #     ORDER BY timestamp ASC
    # """, [sensor_id])

    # data = cursor.fetchall()
    
    # if len(data)==0:
    #     #If this is the case then there is an issue with the logger class' update method
    #     return 'ERR IN DATAPATH'    

def getMean(data):
    pass

def getMax(data):
    pass

def getMin(self, data):
    pass


#print(self.getTimeStamps())
## use GUI to call this 
#Data = Extract_Data()        #     return 'ERR IN DATAPATH'    


#THIS IS THE PROCEDURE TO BE CALLED FROM THE GUI
# Extract_data.initialize_database('139.147.91.185')
# Extract_Data.getDelmiter()
# timeData = Extract_Data.getTimeStamps()
# timeStamps = timeData[0]
# durations = timeData[1]

initialize_database('139.147.91.186')
getDelimiter()
timeData = getTimeStamps()
timeStamps = timeData[0]
durations = timeData[1]