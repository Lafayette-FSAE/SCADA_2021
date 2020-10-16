import smbus2
import time
# Open i2c bus 1 and read one byte from address 80, offset 0

bus = smbus2.SMBus(1)
c= 1
while True:
    try:
        a = bus.read_byte_data(0x77, 0x88, force=None)
        b = bus.read_byte_data(0x77, 0x89, force = None)
        print("Temp" ,(a<<8)+b, " a: ", a, " b: ", b, end = '\r')
        time.sleep(0.25)
        
        #print("After Sleep", c)
        #c=c+1
    except IOError:
        time.sleep(.002)
# c= bus.read_byte_data(0x77, 0xF8, force=None)
# print("LSB",c)
# #
# #val = (b << 8) + c 
# 
# #print("Final Val: " ,val)
bus.close()