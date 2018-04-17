import serial
import time

ser=serial.Serial("/dev/ttyAMA0",9600,timeout=1)

ser.flush()
ser.write('ATD+919999340026;\r')

time.sleep(10)

ser.write('ATH\r')

ser.close()
