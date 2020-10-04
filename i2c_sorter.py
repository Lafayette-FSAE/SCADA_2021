
import sys, os
import config
import smbus2
import redis
import utils
import time
class i2c_sorter:
    #make bus number configurable
    bus = smbus2.SMBUS(1)
    def read(Sensor):
        try:
            if(Sensor.address == 0x68):
                return read_rtc(Sensor)
            else:
                data = ''
                for i in range(len(Sensor.address)):
                    data = str(bus.read_byte(Sensor.address,Sensor.reg_address[i]) << (8 * i-1))+data
                return data
        except IOError:
            time.sleep(.0001)
           # for x in range(start, stop, step)

    def write(Sensor, Value):
        try:
            for i in range(len(str(hex(Value)).replace("0x",""))-1):
                if(i % 2 == 0):
                    #bus.write_byte(Sensor.reg_address[i/2],str(hex(Value))[i-1]+str(hex(Value))[i])
                    bus.write_byte(Sensor.reg_address[i/2],hex(((0xFF << i*4)&Value)>>i*4))
                    # print(str(hex(Value))[i-1]+str(hex(Value))[i])
                    
        except IOError:
            time.sleep(.0001)

    def read_rtc(Sensor)
        data = ""
        seconds_data = ""
        mins_data = ""
        hours_data= ""
        for i in range(len(Sensor.reg_address)):
            busval = bus.read_byte_data(Sensor.address,Sensor.reg_address[i])
            if (i == 0):
                seconds_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF))) 
            if (i == 1):
                mins_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))
            if (i == 2):
                hours_data = str(hex(((busval & 0xF0)>> 4))) + str(hex((busval & 0xF)))
        return (hours_data + ":" + mins_data + ":" + seconds_data).replace("0x","")
        


        

