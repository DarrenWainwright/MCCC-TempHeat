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
parser.add_argument("--config", "-c", type=str, required=True, help="Configuration full name, i.e myconfig.json")
args = parser.parse_args()

print(args)
print("Starting.")

# assign GPIO pin
pin = (board.D4 if args.sensor == 1 else board.D18)

# load config
print("Load config")
with open(args.config) as f:
  config = json.load(f)

# Initiate the event grid topics
print("Initiate Event Grid topics")
eg_topics = Services.EventGrid.CreateOrUpdateTopics(config["eventGrid"]["management"])

# connect to the sensor
print("Connect to sensor..")
dhtDevice = adafruit_dht.DHT22(pin)

# difference constants
TEMP_VARIANT = 0.25
HUMIDITY_VARIANT = 0.25

tempTracker = 0
humidityTracker = 0

print("\nBegin polling sensor..")
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
            data['temperature_c'] =  details.Temperature_C()
            data['temperature_f'] =  details.Temperature_F()

            topicData = eg_topics[eg_topics.index("Temperature")]

            Services.EventGrid.PublishEvent(topicData["topicEndpoint"], topicData["topicKey"], "Temperature Changed Event", "TemperatureChanged", data)
            print(f"Sensor {args.sensor} | Temp {details.Temperature_C()}/c {details.Temperature_F()}/f")
    if details.Humidity() is not None:
        diff = humidityTracker - details.Humidity()
        diff = diff if diff > 0 else diff * -1
        if diff >= HUMIDITY_VARIANT:
            humidityTracker = details.Humidity()
            # Publish Event
            data = {}
            data['sensor_id'] = args.sensor
            data['temperature_c'] =  details.Temperature_C()
            data['temperature_f'] =  details.Temperature_F()

            topicData = eg_topics[eg_topics.index("Humidity")]

            Services.EventGrid.PublishEvent(topicData["topicEndpoint"], topicData["topicKey"], "Temperature Changed Event", "TemperatureChanged", data)
            print(f"Sensor {args.sensor} | Humidity {details.Humidity()}")
    

