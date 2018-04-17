
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime
import logging
import time
import argparse
import json
import random
import bluetooth
import socket
import requests

bd_addr = "00:18:E4:34:E6:BB" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

    
data = ""
bluetooth_payload = [];
total_data_elements = 3
    


AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="a2bxaswjx3x1nz.iot.us-east-1.amazonaws.com")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="rootCA.pem")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="47b65b3ace-certificate.pem")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="47b65b3ace-private.pem.key")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="RasPi3_SDB")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="temperature", help="Payload/topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World from RasPi3",
                    help="Message fromRasPi3")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

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
loopCount = 0
numOfLoops = 5
while loopCount<=numOfLoops :
    try:
        if args.mode == 'both' or args.mode == 'publish':
            data += sock.recv(1024)
            data_end = data.find("\n")
            if data_end != -1:
                rec = data[:data_end]
                bluetooth_payload = data.split(",")
                if len(bluetooth_payload) == total_data_elements:
                    print bluetooth_payload
                    print bluetooth_payload[0]
                    print bluetooth_payload[1]
                    print bluetooth_payload[2]
                    print loopCount
                temp = bluetooth_payload[0]
                hum = bluetooth_payload[1]
                obs_dis = bluetooth_payload[2].replace("\n","")
                data = data[data_end+1:]
        
            message = {}
            message['message'] = args.message
            message['sequence'] = loopCount
            messageJson = json.dumps(message)
            python_object = {
                     'Device_ID': 'RaspberryPi3_cdf7',
                     'time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'Temperature': temp,
                     'Humidity': hum,
                     'Obs_Distance': obs_dis
                            }
            json_string = json.dumps(python_object)
            myAWSIoTMQTTClient.publish(topic,json_string,1)
            if args.mode == 'publish':
                print('Published topic %s: %s\n' % (topic, json_string))
            
        
            loopCount += 1

    except KeyboardInterrupt:
	    break

sock.close()