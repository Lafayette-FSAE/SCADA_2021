##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers:Irwin Frimpong,Harrison Walker,Lia Chrysanthopoulos, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: i2c_driver.py                                                 
## Description: I2C Driver moduule with read and write methods                
#############################################################################################
import sys, os
import smbus
import redis
import time
from datetime import datetime

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config

##########Declariing i2C Bus##############
bus = smbus.SMBus(3) 
##########################################

# read method for I2C Configured sensor 
# @param Sensor - Sensor of Interest
# @return data - Value stored in the secondary register addresses defined in config

def read(Sensor):
    try:
        # Retrieving sensor address from Configuration Yaml File
        sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address') 
        #Use RTC read method if primary address is 0x68 -> RTC
        if( sensor_address == 0x68):
            return read_rtc(Sensor)
        else:
            data = 0
            reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')
            bit_length = config.get('Sensors').get(str(Sensor)).get('bit_length')
            if(bit_length == 8): #Read Byte
                if (type(reg_address) == list): 
                #adds the values for each byte of the sensor together to get the overall result of the sensor
                    for i in range(len(reg_address)):
                        data = data|bus.read_byte_data(sensor_address,reg_address[i]) << (8 * i)
                else: 
                    data = bus.read_byte_data(sensor_address,reg_address) 
            else: # Read Word
                data = bus.read_word_data(sensor_address,reg_address)
                                
        return data
    except IOError:
        time.sleep(.0001)

# write method for I2C driver writes specifed value to the sensor 
# @param Sensor - Sensor of Interest
# @param Value - Value to written to the sensor

def write(Sensor, Value):
    try:
        #Use RTC write method if primary address is 0x68 -> RTC
        sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address')
        if(sensor_address == 0x68):
            return write_rtc(Sensor,Value)
        else:
            #Obtaining reg_adress list from Config YAML file
            reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')
            numofBits = countTotalBits(Value)

            if(numofBits <= 8): #Use write_byte_data to write 8 bits
                bus.write_byte_data(sensor_address,reg_address,Value)
            else: #Use write_word_data to write value in 16 bits
                bus.write_word_data(sensor_address,reg_address,Value)

    except IOError:
        time.sleep(.0001)

# read_rtc method for PCF-8523 RTC which reads the (month,day,year,hour,minutes,seconds) registers of the 
# rtc and returns unix time 
# @param Sensor - Sensor input of interest
# @return Unix Time of RTC

def read_rtc(Sensor):
    data = ""
    seconds_data = ""
    mins_data = ""
    hours_data= ""

    try:
        sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address') 
        reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')
        FMT = '%Y-%m-%d %H:%M:%S'

        for i in range(len(config.get('Sensors').get(str(Sensor)).get('secondary_address'))):
            busval = bus.read_byte_data(sensor_address,reg_address[i])
            if (i == 0):
                seconds_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF))) 
            elif (i == 1):
                mins_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))
            elif (i == 2):
                hours_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))
            elif (i == 3):
                days_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF))) 
            elif (i == 4):
                months_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))
            elif (i == 5):
                years_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))

        time_str = ("20"+ years_data + "-" + months_data + "-" + days_data + " " + hours_data + ":" + mins_data + ":" + seconds_data).replace("0x","")
        return datetime.strptime(time_str, FMT).timestamp()
        #return (hours_data + ":" + mins_data + ":" + seconds_data).replace("0x","")

    except IOError:
        time.sleep(.0001)


# write_rtc method for PCF-8523 RTC which writes in year,month,day,hour,minutes,seconds into their respective registers 
# @param Sensor - Sensor input of interest
# @param Value - 'YR:MO:DD:HR:MI:SS' How we want value to be inputted
def write_rtc(Sensor,Value):
    val=Value.split(":")
    
    #Obtaining Primary and Secondary Addresses from Config YAML
    sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address') 
    reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')
    try:
        bus.write_byte_data(sensor_address,reg_address[0],int(val[0],16)) #Year Resgiter Address
        bus.write_byte_data(sensor_address,reg_address[1],int(val[1],16)) #Month Register Address
        bus.write_byte_data(sensor_address,reg_address[2],int(val[2],16)) #Day Register Address
        bus.write_byte_data(sensor_address,reg_address[3],int(val[3],16)) #Hours Register Address
        bus.write_byte_data(sensor_address,reg_address[4],int(val[4],16)) #Minutes Register Address 
        bus.write_byte_data(sensor_address,reg_address[5],int(val[5],16)) #Second Register Address
       
    except IOError:
        time.sleep(.0001)

#countTotalBits method finds the number of bits used to represent a number. This function to be used in the write i2c write method
# @param num - Number of interest
# @return Number of bits needed to represent the num input in binary
def countTotalBits(num):
     #convert number into it's binary and remove first two characters 0b.
     binary = bin(num)[2:]
     return len(binary)


    
        


        

