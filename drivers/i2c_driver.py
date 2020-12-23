import sys, os
import config
import smbus
import redis
import utils
import time

#Declariing i2C Bus
bus = smbus.SMBus(1)

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
            #adds the values for each byte of the sensor together to get the overall result of the sensor
            for i in range(len(reg_address)):
                #data = data + bus.read_byte_data(sensor_address,reg_address[i]) << (8 * i)
                # Using Bitwise And Instead here 
                data = data|bus.read_byte_data(sensor_address,reg_address[i]) << (8 * i)
                                
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
            bus.write_byte_data(sensor_address,reg_address,Value)
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

        #return (years_data + ":" + months_data + ":" + days_data + ":" + hours_data + ":" + mins_data + ":" + seconds_data).replace("0x","")
        return (hours_data + ":" + mins_data + ":" + seconds_data).replace("0x","")

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


    
        


        

