#!/usr/bin/env python
# -*- coding: utf-8 -*-

#https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
"""Module monitors temperature and humidity.
   Results are published to the event grid via the config file.

   Part of the Mother Cluckers Coop Control project
"""
import argparse, time, json, threading
import adafruit_dht
import Services

#TODO// - Can't seem to get this working on windows. adafruit_blinka or RPi.GPIO won't install
import board

# Initialize method. Sets up event grid topics and returns them
def Initialize(sensor, config):    
   
    # Initiate the event grid topics
    print("Initiate Event Grid topics")
    mgmt = config["eventGrid"]["management"]
    return Services.EventGrid.GetEventGridTopics(mgmt["azureTenantId"]
                                                        ,mgmt["subscriptionId"]
                                                        ,mgmt["resourceGroupName"]
                                                        ,mgmt["location"]
                                                        ,mgmt["azureClientId"]
                                                        ,mgmt["azureClientSecret"]
                                                        ,mgmt["topicNames"])

# Processes the sensor events and publishes to the event grid
def ProcessSensorEvents(topics, sensor, name, config):
    # assign GPIO pin
    pin = (board.D4 if sensor == 1 else board.D18)

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

    # difference constants
    TEMP_VARIANT = 0.25
    HUMIDITY_VARIANT = 0.25

    tempTracker = 0
    humidityTracker = 0

    publish = config["eventGrid"]["enablePublish"]

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
                data['name'] = name
                data['temperature_c'] =  details.Temperature_C()
                data['temperature_f'] =  details.Temperature_F()
                print("Temperature Changed")
                topicData = topics["Temperature"]
                if publish == True:
                    print(f"Publish {topicData.Name()} Topic Data: Endpoint = {topicData.Endpoint()} | Key = {topicData.Key()} | Data = {data}")
                    Services.EventGrid.PublishEvent(topicData.Endpoint(), topicData.Key(), "Temperature Changed Event", "TemperatureChangedEvent", data)
                print(f"Temperature Sensor {sensor} | Temp {details.Temperature_C()}/c {details.Temperature_F()}/f")
        if details.Humidity() is not None:
            diff = humidityTracker - details.Humidity()
            diff = diff if diff > 0 else diff * -1
            if diff >= HUMIDITY_VARIANT:
                humidityTracker = details.Humidity()
                # Publish Event
                data = {}
                data['sensor_id'] = sensor
                data['name'] = name
                data['humidity'] =  details.Humidity()
                print("Humidity Changed")
                topicData = topics["Humidity"]
                if publish == True:
                    print(f"Publish {topicData.Name()} Topic Data: Endpoint = {topicData.Endpoint()} | Key = {topicData.Key()} | Data = {data}")           
                    Services.EventGrid.PublishEvent(topicData.Endpoint(), topicData.Key(), "Humidity Changed Event", "HumidityChangedEvent", data)
                print(f"Humidity Sensor {sensor} | Humidity {details.Humidity()}")
        
# Publish heartbeat events every n-seconds
def Heartbeat(heartbeatTopic, sensor, name, config):
    print("Begin heartbeat")
    secs = config["heartbeat"]
    # Publish Event
    data = {}
    data['type'] = 'DHT22'
    data['name'] = name
    data['heartbeat_interval'] = secs
    publish = config["eventGrid"]["enablePublish"]
    
    while True:
        if publish == True:
            print(f"Publish {heartbeatTopic.Name()} Topic Data: Endpoint = {heartbeatTopic.Endpoint()} | Key = {heartbeatTopic.Key()} | Data = {data}")           
            Services.EventGrid.PublishEvent(heartbeatTopic.Endpoint(), heartbeatTopic.Key(), "Heartbeat Event", "HeartbeatEvent", data)       
        else:
            print("* * Heartbeat * * ")
        time.sleep(secs)

    

##########################################
# Start here
##########################################

# setup & parse input parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sensor", "-s", type=int, required=True, choices=[1,2], help="Sensor number. Supported values are 1 or 2")
parser.add_argument("--name", "-n", type=str, required=True, help="Sensors name")
parser.add_argument("--config", "-c", type=str, required=True, help="Configuration full name, i.e myconfig.json")
args = parser.parse_args()

print(f"DHTxx Sensor #{args.sensor} started")

 # load config
print(f"Loding config file {args.config}")
with open(args.config) as f:
    config = json.load(f)


topics = Initialize(args.sensor, config)

sThread = threading.Thread(target=ProcessSensorEvents, args=(topics, args.sensor, args.name, config), daemon=True)
hThread = threading.Thread(target=Heartbeat, args=(topics["Heartbeat"], args.sensor, args.name,config), daemon=False)

sThread.start()
hThread.start()