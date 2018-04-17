import serial
import RPi.GPIO as GPIO
import os, time

GPIO.setmode(GPIO.BOARD)

# Enable Serial Communication
port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key
print 'cmd1'
port.write('AT'+'\r\n')
rcv = port.read(10)
print rcv
time.sleep(1)

print 'cmd2'
port.write('ATE0'+'\r\n')      # Disable the Echo
rcv = port.read(10)
print rcv
time.sleep(1)

print 'cmd3'
port.write('AT+CMGF=1'+'\r\n')  # Select Message format as Text mode 
rcv = port.read(10)
print rcv
time.sleep(1)

print 'cmd4'
port.write('AT+CNMI=2,1,0,0,0'+'\r\n')   # New SMS Message Indications
rcv = port.read(10)
print rcv
time.sleep(1)

# Sending a message to a particular Number
print 'cmd5'
port.write('AT+CMGS="+917297968170"'+'\r\n')
rcv = port.read(10)
print rcv
time.sleep(1)

print 'cmd6'
port.write('Hello Akshay'+'\r\n')  # Message
rcv = port.read(10)
print rcv

print 'cmd7'
port.write("\x1A") # Enable to send SMS
for i in range(10):
    rcv = port.read(10)
    print rcv
