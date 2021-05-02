import sys, os
import smbus
import redis
import utils
import time
from datetime import datetime

#CONFIG PATH
lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

sys.path.append(lib_path)
sys.path.append(config_path)

import config

#Declariing i2C Bus
bus = smbus.SMBus(3) ##CHNAGED BUS to 3 for debigging

# General i2c Read Method
def read(Sensor):
    try:
        #Use RTC read method if primary address is 0x68 -> RTC
        sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address') 
        if( sensor_address == 0x68):
            return read_rtc(Sensor)
        else:
            data = 0
            reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')

            if (type(reg_address) == list): 
            #adds the values for each byte of the sensor together to get the overall result of the sensor
                for i in range(len(reg_address)):
                #data = data + bus.read_byte_data(sensor_address,reg_address[i]) << (8 * i)
                # Using Bitwise And Instead here 
                    data = data|bus.read_byte_data(sensor_address,reg_address[i]) << (8 * i)
            else: 
                data = bus.read_byte_data(sensor_address,reg_address) 
                                
            return data
    except IOError:
        time.sleep(.0001)

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

#Read function for RTC pcf-8523
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


#Write Function for RTC to set date and time
def write_rtc(Sensor,Value):
    # 'YR:MO:DD:HR:MI:SS' How we want value to be inputted
    val=Value.split(":")
    
    #Obtaining Primary and Secondary Addresses from Config YAML
    sensor_address = config.get('Sensors').get(str(Sensor)).get('primary_address') 
    reg_address = config.get('Sensors').get(str(Sensor)).get('secondary_address')
    try:
        bus.write_byte_data(sensor_address,reg_address[0],int(val[0],16)) #Year
        bus.write_byte_data(sensor_address,reg_address[1],int(val[1],16)) #Mont
        bus.write_byte_data(sensor_address,reg_address[2],int(val[2],16)) #Daysensor_address
        bus.write_byte_data(sensor_address,reg_address[3],int(val[3],16)) #Hours
        bus.write_byte_data(sensor_address,reg_address[4],int(val[4],16)) #Minutes
        bus.write_byte_data(sensor_address,reg_address[5],int(val[5],16)) #Second

    
    except IOError:
        time.sleep(.0001)

#Function to find the number of bits used to represent a number. This function to be used in the write i2c write method
def countTotalBits(num):
     #convert number into it's binary and remove first two characters 0b.
     binary = bin(num)[2:]
     return len(binary)


    
        


        

