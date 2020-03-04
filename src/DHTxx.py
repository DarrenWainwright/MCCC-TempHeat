#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module monitors temperature and humidity.
   Results are published to the eventUrl, eventType arguments

   Part of the Mother Cluckers Coop Control project
"""
import argparse, time

parser = argparse.ArgumentParser()

parser.add_argument("--event-url", "-u", help="Sets the event grid topic url")
parser.add_argument("--event-type", "-t", help="Sets the event type [poll,auto,temp,humidity]")

args = parser.parse_args()



print("argList: %s" % args)
