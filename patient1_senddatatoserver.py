from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import bluetooth
from datetime import datetime
import json
import pi_gsm_intrfc
import requests
import socket
import time

def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

#root_dir="/home/pi/Desktop/ses_final_project/"
bd_addr = "00:15:83:35:8B:40" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

awshost="a1gncii32ntyvu.iot.us-east-2.amazonaws.com"	#AWS endpoint
awsport=8883						#AWS port
client_id="ses_rpi"					#thing name
thing_name="ses_rpi"					#thing name
ca_path="root-CA.crt"					#root certificate path
cert_path="ses_rpi.cert.pem"				#certificate path
privkey_path="ses_rpi.private.key"			#private key
topic_name="ses_rpi/topic"

# thingspeak server details
patient_name = 'Akshay'
api_key = 'HXUUEPLERWVN2PS3'
thingspeak_url = 'https://api.thingspeak.com/update'


AllowedActions = ['both', 'publish', 'subscribe']

# adding endpoint details, thing_name etc
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help=awshost)
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help=ca_path)
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help=cert_path)
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help=privkey_path)
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help=client_id)
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help=topic_name)
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World from Rpi3 !!",
                    help="Sending sensor data to AWS !!")

# fetch arguments
args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)


# Publish to the same topic in a loop forever
data = ""
loopCount = 0
noOfLoops = 5
total_data_elements = 7

while loopCount < noOfLoops:
    if args.mode == 'both' or args.mode == 'publish':
        try:
            
            # receive data from bluetooth
            data += sock.recv(2048)
            data_end = data.find("\n")
            if data_end != -1:
		rec = data[:data_end]
		payload = data.split(",")
                payload[6] = payload[6].split("\n")[0]

		data = data[data_end+1:]

            # create JSON object for sending messages
            message = {}
            message['message'] = args.message
            message['sequence'] = loopCount
            messageJson = json.dumps(message)
            python_object = {
                     'Device_ID': 'Rpi3',
                     'time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'Temperature': str(float(payload[0]) / 100),
                     'PulseRate': payload[1],
                     'Latitude': payload[2],
                     'Longitude': payload[3],
                     'AccX': payload[4],
                     'AccY': payload[5],
                     'AccZ': payload[6],
                     'patient_name': patient_name
                            }
            json_string = json.dumps(python_object)
            myAWSIoTMQTTClient.publish(topic,json_string,1)
            if args.mode == 'publish':
                print('Published topic %s: %s\n' % (topic, json_string))

            # send data to thingspeak server
            ts_payload = {'api_key':api_key, 'field1':str(float(payload[0]) / 100),'field2':payload[1], 'field3':payload[4],'field4':payload[5],'field5':payload[6]}
            req = requests.post(thingspeak_url, params=ts_payload)
            print ("TS success status:", req.text)
            time.sleep(30)

            
            loopCount = loopCount + 1
            temperature = float(payload[0]) / 100
            if temperature > 0:
                pi_gsm_intrfc.send_sms(patient_name)

        
        except KeyboardInterrupt:
            break

        # pause between 2 consecutive writes
        time.sleep(1)

sock.close()
