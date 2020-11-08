#!/usr/bin/python3

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
os.system('sudo xhost +')
os.system('sudo export DISPLAY=":0.0"')
os.system('sudo python3 /usr/bin/scada_gui.py')

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
p.subscribe('new-session')

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
CREATE TABLE IF NOT EXISTS sensors(
    id SERIAL PRIMARY KEY,
    redis_key VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    datatype VARCHAR(255),
    unit VARCHAR(255)
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
    # Harry: This is the statement that has tabulation errors
    # Harry: THE REASON IS RANDOM SPACES AND INDENTS AFTER THE "INSERT INTO" LINE
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

def update(message, key):
    # Don't log the value if an identical
    # value has been logged recently
    # message = calculated_data
    # {sensern_name}:{calculated_data}

    split_key = key.split(":")
    Sensor_value= split_key[1]
    Sensor_key = split_key[0]
    if not check_update_ready(Sensor_key,Sensor_value):
        return

  #   # Harry: Builds list of all the ignore keys (why is it doing this every time it updates??)
    ignore_keys = []
#     for key_string in config.get('dont_log', []):
#         ignore_keys = ignore_keys + redis_data.keys(key_string)
    
    if not key in ignore_keys:
        # Harry: attempts to put sensor key in the sensor table if not already
        # Harry: WHY IS THIS DONE ON EVERY UPDATE? This should be in the config.py, right?
        # Harry: Unless the idea here is to only have sensor info for the sensors involved in any
        #        data session. Seems inefficient though.
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

        # updates previous value/timestamp for check_update_ready method on next loop
        previous_values[Sensor_key] = (Sensor_value, datetime.datetime.now())

        # I think this method should call "database.commit()" here

# Harry: THIS IS THE ACTUAL CODE THAT RUNS

while True:
    # Harry: Redis object gets the next message from its subscribed channels if one is available
    # Harry: Note: this "message" object is just a dict with keys 'type', 'pattern', 'channel', and 'data'
    message = p.get_message()
    #Debugging Comments
    print(message)
    if (message and (message['data'] != 1 )):
        # Harry: calls update method (checks if it should be logged and executes database queries to log it)
        if message['channel'] in ['calculated_data']:  
            update(message['channel'], message['data'])
            #Harry: to get live view, we could print the "previous_values" table here
        elif message['channel'] == 'new-session':
            delimit_session()        

    # Harry: if no messages available, commit changes to database and wait for next loop
    else:
        database.commit()
        time.sleep(0.1)
