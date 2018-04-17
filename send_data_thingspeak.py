#!/usr/bin/python

import requests
import time
import random

api_key = 'HXUUEPLERWVN2PS3'
latitude = '28.380210'
longitude = '75.609170'
thingspeak_url = 'https://api.thingspeak.com/update'

def send_data(payload):
    # data in thinkspeak will go in JSON format
    req = requests.post(thingspeak_url, params=payload)
    print ("Success status:", req.text)
    time.sleep(30)
    

def main():
    # create a patient dictionary, that'll contain temperature and pulse rate data
    akshay={};
    for i in range(1,6):
        akshay['temperature'] = random.randint(37, 41)
        akshay['pulse_rate'] = random.randint(90, 100)
        print 'Sending ',akshay['temperature'], akshay['pulse_rate']
        payload = {'api_key':api_key, 'field1':str(akshay['temperature']), 'field2':str(akshay['pulse_rate']), 'latitude':str(latitude), 'longitude':longitude}
        send_data(payload)
        

if __name__ == '__main__':
    main()
    