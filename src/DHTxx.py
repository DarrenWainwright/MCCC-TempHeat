#!/usr/bin/env python
# -*- coding: utf-8 -*-

#https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup

"""Module monitors temperature and humidity.
   Results are published to the eventUrl, eventType arguments

   Part of the Mother Cluckers Coop Control project
"""
import argparse, time
import adafruit_dht
from Services import Sensor

#TODO// - Can't seem to get this working on windows. adafruit_blinka or RPi.GPIO won't install
import board

# setup & parse input parameters
parser = argparse.ArgumentParser()
parser.add_argument("--sensor", "-s", type=int, required=True, choices=[1,2], help="Sensor number. Supported values are 1 or 2")
args = parser.parse_args()

# assign GPIO pin
pin = (board.D4 if args.sensor == 1 else board.D18)

# connect to the sensor
dhtDevice = adafruit_dht.DHT22(pin)


while True:
    details = Sensor.GetDetails(dhtDevice, 5)
    if details.Temperature_C is not None:
        print(f"Temp {details.Temperature_C()}/C {details.Temperature_F()}/F: Humidity {details.Humidity()}")
    else:
        print("didn't work")

