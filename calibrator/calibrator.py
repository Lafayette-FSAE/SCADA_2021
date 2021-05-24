#!/usr/bin/python3
##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Harrison Walker, Adam Tunnell, Irwin Frimpong,Lia Chrysanthopoulos, Mithil Shah                                 
## Last Updated : 05/12/2021 11:06 AM                       
## Project Name: SCADA FSAE 2021                                 
## Module Name: calibrator.py                                                 
## Description: calibrator.py module calibrates raw data values of sensors using the specified
##              calibrartion functions in the configuration file.
#############################################################################################

import sys, os
import redis
import time
import datetime

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config 
import utils


# TODO: reintroduce verbose logging

# Configure Redis interface For Raw Sensors Data
data = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
p = data.pubsub()
p.subscribe('raw_data')

#Local Dictionary storing values of Calibrated Sensors used for Virtual Sensors
last_calc_vals = {}

#Performs Calibration on Raw Sensor Values. Sensor_val[0] is the sensor name and Sensor_val[1] is the raw sensor value that needs to be calibrated.
def execute(Sensor_val):
    #Retrieve Calibration Function From Yaml Configuration File
    calibration_func = config.get('Sensors').get(Sensor_val[0]).get('cal_function')
    output = ''

    #Debuggin
    # print(str(Sensor_val[0]) +":  Sensor Value: " + Sensor_val[1] )

    if (Sensor_val[1] == 'no data'): 
        output = 'no data'
        last_calc_vals[Sensor_val[0]] = output
    else:
        if type(calibration_func) is not str and type(list(calibration_func.keys())[0]) is str:
            cal_func_set = False
            for key in calibration_func:
                new_key = key
                for input_key in config.get('Sensors').get(Sensor_val[0]).get('inputs'):
                    #new_key = new_key.replace(input_key,str(last_calc_vals[config.get('Sensors').get(Sensor_val[0]).get('inputs').get(input_key)]))
                    new_key = new_key.replace(input_key,str(Sensor_val[1])) # Debiggin -- this should the case for sensors that are not virutal with comditional calibration
                if (eval(new_key) == True and cal_func_set == False):
                    calibration_func = calibration_func[key]
                    cal_func_set = True
        

        for key in config.get('Sensors').get(Sensor_val[0]).get('inputs'):
            calibration_func = calibration_func.replace(key,Sensor_val[1])
    
        calibrated_eval = eval(calibration_func)
        #Getting Precision Specificed for Sensor for Printing 
        precision = config.get('Sensors').get(Sensor_val[0]).get('precision')
        format_var = "{0:."+str(precision)+'f}'
        output= format_var.format(calibrated_eval)
        #Adding Value of Calibrated Sensor to Local Dictionary 
        last_calc_vals[Sensor_val[0]] = output

    return(output)

#Method to peform Calibration on virtual sensors. Sensor_val[0] is the sensor name and Sensor_val[1] is the raw sensor value that needs to be calibrated.
def Virtual_execute(Sensor_val):
    output = ''
    # Line Below used for Debugging
    # print(str(Sensor_val[0]) +":  Sensor Value: " + Sensor_val[1] )
    no_data_bolean = False
    retrived_input = ''
    calibration_func = config.get('Sensors').get(Sensor_val[0]).get('cal_function')

#For Conditional Calibration Functions
    if type(calibration_func) is not str and type(list(calibration_func.keys())[0]) is str:
        cal_func_set = False
        for key in calibration_func:
            new_key = key
            for input_key in config.get('Sensors').get(Sensor_val[0]).get('inputs'):
                input_key_val= str(last_calc_vals[config.get('Sensors').get(Sensor_val[0]).get('inputs').get(input_key)])
                if (input_key_val == 'no data'):
                    no_data_bolean = True
                new_key = new_key.replace(input_key,input_key_val)
            if (no_data_bolean == False and eval(new_key) == True and cal_func_set == False):
                calibration_func = calibration_func[key]
                cal_func_set = True
    
    if not no_data_bolean:           
        for key in config.get('Sensors').get(Sensor_val[0]).get('inputs'):
            try:
                retrived_input = str(last_calc_vals[config.get('Sensors').get(Sensor_val[0]).get('inputs').get(key)])
            except KeyError:
                retrived_input = 'no data'
                break
            calibration_func = calibration_func.replace(key,retrived_input)

    if (no_data_bolean or retrived_input == 'no data'):
        output = 'no data'
    else: 
        calibrated_eval = eval(calibration_func)
        precision = config.get('Sensors').get(Sensor_val[0]).get('precision')
        format_var = "{0:."+str(precision)+'f}'
        output= format_var.format(calibrated_eval)
        last_calc_vals[Sensor_val[0]] = output
      
    return(output)

#Method to perform Calibration on State Sensors. Sensor_val[0] is the sensor name and Sensor_val[1] is the raw sensor value that needs to be calibrated. 
def State_execute(Sensor_val):
    output = '' 
    #Retrieving Calibrated State from YAML
    #print("STATE CAL FUNCTION:")
    #print(config.get('Sensors').get(Sensor_val[0]).get('cal_function'))
    if (Sensor_val[1] == 'no data'):
        output = 'no data'
    else:
        output = config.get('Sensors').get(Sensor_val[0]).get('cal_function').get(int(Sensor_val[1]))
   
    return (output)

#Method to perform Calibration on String Display Variables. Sensor_val[0] is the sensor name and Sensor_val[1] is the raw sensor value that needs to be calibrated.
def String_execute(Sensor_val):
    output = ''
    calibration_func = config.get('Sensors').get(Sensor_val[0]).get('cal_function')

    if (Sensor_val[1] == 'no data'):
        output = 'no data'
    else:    
        for key in config.get('Sensors').get(Sensor_val[0]).get('inputs'):
            output = calibration_func.replace(key,Sensor_val[1])

    return (output)


#Method publishes calibrated data to the Calculated Data Redis Channel      
def update(sensor_key):
    split_key = sensor_key.split(":",1)
    print ("Split KEY : " + split_key[0]) #SpLiT kEy
    
    if split_key[1] == 'bus error':
        data.publish('calculated_data', '{}:{}'.format(split_key[0], 'BUS ERROR'))

    #Check For Display Variable to Differientiate between states and number values 
    elif config.get('Sensors').get(split_key[0]).get('display_variable') == 'state':
        data.publish('calculated_data', '{}:{}'.format(split_key[0], str(State_execute(split_key))))
    
    elif config.get('Sensors').get(split_key[0]).get('display_variable') == 'string':
        data.publish('calculated_data', '{}:{}'.format(split_key[0], str(String_execute(split_key))))

    #Display Variable is a number and can be calibrated with functions 
    else: 
    #Checking the Length of the inputs dictionary from YAML file
    #Bus Type (CAN & I2C) - Raw Sensor Calibration Method Called 
    #Else - Virtual Sensor Calibration Method Called 
        if config.get('Sensors').get(split_key[0]).get('bus_type') != 'VIRTUAL':
            data.publish('calculated_data', '{}:{}'.format(split_key[0], str(execute(split_key)) ))
        else:
            data.publish('calculated_data', '{}:{}'.format(split_key[0], str(Virtual_execute(split_key))))
        

#Listening to the Calculated Data Channel for New Messages 
while True:
    message = p.get_message() 
    if (message and (message['data'] != 1 )):
        update(message['data'])
    else:
        time.sleep(0.1)



