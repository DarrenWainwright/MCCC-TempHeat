#!/usr/bin/env python
# -*- coding: utf-8 -*-

#https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup

"""Module monitors temperature and humidity.
   Results are published to the event grid via the config file.

   Part of the Mother Cluckers Coop Control project
"""
import argparse, time, json
import adafruit_dht
import Services

#TODO// - Can't seem to get this working on windows. adafruit_blinka or RPi.GPIO won't install
import board

# setup & parse input parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sensor", "-s", type=int, required=True, choices=[1,2], help="Sensor number. Supported values are 1 or 2")
parser.add_argument("--name", "-n", type=str, required=True, help="Sensors name")
parser.add_argument("--config", "-c", type=str, required=True, help="Configuration full name, i.e myconfig.json")
args = parser.parse_args()

print(f"DHTxx Sensor #{args.sensor} started")

# assign GPIO pin
pin = (board.D4 if args.sensor == 1 else board.D18)

# connect to the sensor
print("Connecting to sensor..")
dhtDevice = adafruit_dht.DHT22(pin)

# Wait until it is connected before continuing
connected = False
while not connected:
    time.sleep(2)
    try:        
        if dhtDevice.measure() == None:
            connected = True
    except Exception as identifier:
        print("Waiting for sensor..")
        pass

print("Sensor detected. Continuing.")

# load config
print(f"Loding config file {args.config}")
with open(args.config) as f:
  config = json.load(f)

# Initiate the event grid topics
print("Initiate Event Grid topics")
mgmt = config["eventGrid"]["management"]
eg_topics = Services.EventGrid.GetEventGridTopics(mgmt["azureTenantId"]
                                                    ,mgmt["subscriptionId"]
                                                    ,mgmt["resourceGroupName"]
                                                    ,mgmt["location"]
                                                    ,mgmt["azureClientId"]
                                                    ,mgmt["azureClientSecret"]
                                                    ,mgmt["topicNames"])




# difference constants
TEMP_VARIANT = 0.25
HUMIDITY_VARIANT = 0.25

tempTracker = 0
humidityTracker = 0

print("Listening to the sensor...")
while True:
    details = Services.Sensor.GetDHTxxDetails(dhtDevice, 5)
    if details.Temperature_C() is not None:
        diff = tempTracker - details.Temperature_C()
        diff = diff if diff > 0 else diff * -1
        if diff >= TEMP_VARIANT:
            tempTracker = details.Temperature_C()
            # Publish Event
            data = {}
            data['sensor_id'] = args.sensor
            data['name'] = args.name
            data['temperature_c'] =  details.Temperature_C()
            data['temperature_f'] =  details.Temperature_F()
            print("Temperature Changed")
            topicData = eg_topics["Temperature"]
            print(f"Publish {topicData.Name()} Topic Data: Endpoint = {topicData.Endpoint()} | Key = {topicData.Key()} | Data = {data}")
            Services.EventGrid.PublishEvent(topicData.Endpoint(), topicData.Key(), "Temperature Changed Event", "TemperatureChangedEvent", data)
            print(f"Temperature Sensor {args.sensor} | Temp {details.Temperature_C()}/c {details.Temperature_F()}/f")
    if details.Humidity() is not None:
        diff = humidityTracker - details.Humidity()
        diff = diff if diff > 0 else diff * -1
        if diff >= HUMIDITY_VARIANT:
            humidityTracker = details.Humidity()
            # Publish Event
            data = {}
            data['sensor_id'] = args.sensor
            data['name'] = args.name
            data['humidity'] =  details.Humidity()
            print("Humidity Changed")
            topicData = eg_topics["Humidity"]
            print(f"Publish {topicData.Name()} Topic Data: Endpoint = {topicData.Endpoint()} | Key = {topicData.Key()} | Data = {data}")           
            Services.EventGrid.PublishEvent(topicData.Endpoint(), topicData.Key(), "Humidity Changed Event", "HumidityChangedEvent", data)
            print(f"Humidity Sensor {args.sensor} | Humidity {details.Humidity()}")
    

