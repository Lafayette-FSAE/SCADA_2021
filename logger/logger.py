#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Lia Chrysanthopoulos, Mithil Shah,Irwin Frimpong                                   
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: logger.py                                                 
## Description: logger module with method used to write sensor data into postgresql database                    
#############################################################################################

import sys
import os
import datetime
import time
import psycopg2
import redis

lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

# import dependent python libraries
import config

#Starting Up the GUI Realtime Display
# os.system('sudo xhost +')
# os.system('export DISPLAY=":0.0"')
# os.system('sudo python3 /usr/bin/scada_gui.py')

# creates instance of Redis
redis_data = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# connection object that connects to Postrges database (NEEDS TO BE CHANGGED)
database = psycopg2.connect(
    user='pi',
    password='scada',
    host='localhost',
    port='5432',
    database='test'
)

# creates Publish/Subscribe Redis object called 'p'
p = redis_data.pubsub()
# p subscribes to get messages from 2 channels in Redis
p.subscribe('calculated_data')
p.subscribe('new-session') #this is from an old implementation of delimiting sessions, now we do it after the fact in Postman
#we left it here in case future teams want to return to that method 
p.subscribe('logs')

# create Postrgres database cursor
#  a cursor is like a dummy user in a database that executes commands and retrieves results
cursor = database.cursor()

# Uncomment this to wipe the database on startup of
# this script, sometimes useful when debugging
#
# cursor.execute("""
#   DROP TABLE IF EXISTS sensors;
#   DROP TABLE IF EXISTS data;
# """)

# Make sure both of our tables exist before starting
cursor.execute("""
CREATE TABLE IF NOT EXISTS data(
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    value VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW()
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs(
    id SERIAL PRIMARY KEY,
    message VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW()
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors(
    id SERIAL PRIMARY KEY,
    redis_key VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    datatype VARCHAR(255),
    unit VARCHAR(255),
    sample_period REAL
);
""")

# commits transactions above to the database
database.commit()


def delimit_session():
    """
        Insert a session delimiter into the data table.
        This is a row with sensor_id of "scada:session"
        and value of "NEW-SESSION"
    """
    
    # This is the statement that has tabulation errors
    # THE REASON IS RANDOM SPACES AND INDENTS AFTER THE "INSERT INTO" LINE
    cursor.execute("""
        INSERT INTO data (sensor_id, value)
        VALUES ('scada:session', 'NEW-SESSION');
    """)


# initializes dictionary that will hold all the previous values from any "key"
#Local Dictionary used for duplicate checking in the PostgresDB
previous_values = {}

def check_update_ready(key,sensor_value):
    """
        For a given key, determine if a new row should be added
        to the data table or not. It does this by checking the
        key against a locally stored dictionary of recently logged
        keys, called previous_values. The dictionary stores both the
        last value logged and the time it was logged. The function
        will return true if either the values are different, or if
        it has been more than a minute since the key was logged last.
    """

    #Key is the name of the sensor
    value, timestamp = previous_values.get(key, (None, datetime.datetime.now()))

    # Always update if the current and previous values are different
    if value != sensor_value:
        return True

    # If they are the same, only update if a set amount of time has elapsed
    elapsed_time = datetime.datetime.now() - timestamp
    if elapsed_time > datetime.timedelta(seconds=60):
        return True
    
    # default
    return False

def update(msgData):
    # Don't log the value if an identical
    # value has been logged recently
    # msgData = contents of redis message
    # {sensor_name}:{calculated_data}

    split_msg = msgData.split(":",1)
    Sensor_value= split_msg[1]
    Sensor_key = split_msg[0]
    if not check_update_ready(Sensor_key,Sensor_value):
        return

  #   # Builds list of all the ignore keys (why is it doing this every time it updates??)
    ignore_keys = []
    #commented out for efficiency. we aren't using any 'ignore keys' at the moment
#     for key_string in config.get('dont_log', []):
#         ignore_keys = ignore_keys + redis_data.keys(key_string)
    
    #Check is sensor name is not in ignore keys and whether sensor data is 'no data' before storing in database 
    if not Sensor_key in ignore_keys:
    
        cursor.execute("""
            INSERT INTO sensors
            (redis_key)
            VALUES (%s)
            ON CONFLICT (redis_key) DO NOTHING
        """, [Sensor_key])
        
        # adds data to data table
        cursor.execute("""
            INSERT INTO data (sensor_id, value)
            VALUES (%s, %s)
        """, [Sensor_key, Sensor_value])

        #publish data to update GUI
        redis_data.publish('logger_data', msgData)

        # updates previous value/timestamp for check_update_ready method on next loop
        previous_values[Sensor_key] = (Sensor_value, datetime.datetime.now())


def update_logs(msgData):
    # adds data to data table
    cursor.execute("""
        INSERT INTO logs (message)
        VALUES (%s)
    """, [msgData])


while True:
    # Redis object gets the next message from its subscribed channels if one is available
    # Note: this "message" object is just a dict with keys 'type', 'pattern', 'channel', and 'data'
    message = p.get_message()
    #Debugging Comments
    #print(message)
    if (message and (message['data'] != 1 )):
        # Calls update method (checks if it should be logged and executes database queries to log it)
        if message['channel'] in ['calculated_data']:
            update(message['data'])
        elif message['channel'] in ['new-session']:
            delimit_session()
        elif (message['channel'] in ['logs'] and message['data'] != 3):
            update_logs(message['data'])

    # if no messages available, commit changes to database and wait for next loop
    else:
        database.commit()
        time.sleep(0.1)
