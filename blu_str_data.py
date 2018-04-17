import bluetooth
import socket
import requests
import time

bd_addr = "00:15:83:35:8B:40" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

    
data = ""
payload = [];
total_data_elements = 7
api_key = 'HXUUEPLERWVN2PS3'
latitude = '28.380210'
longitude = '75.609170'
thingspeak_url = 'https://api.thingspeak.com/update'

def sendDataToServer(payload):
    # data in thinkspeak will go in JSON format
    payload = {'api_key':api_key, 'field1':str(int(payload[0])/100), 'field2':str(float(payload[1]) + 915.0), 'latitude':str(latitude), 'longitude':longitude}
    req = requests.post(thingspeak_url, params=payload)
    print ("Success status:", req.text)
    print ("Waiting for 30 secs...")
    time.sleep(30)
    

while True:
	try:
            data += sock.recv(2048)
            data_end = data.find("\n")
            if data_end != -1:
		rec = data[:data_end]
		payload = data.split(",")
		if len(payload) == total_data_elements:
                    print payload
                    print 'Sending recent data to server...'
                    sendDataToServer(payload)

		data = data[data_end+1:]
		
	except KeyboardInterrupt:
		break

sock.close()
