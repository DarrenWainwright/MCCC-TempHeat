# Mother Cluckers Coop Control - Temp & Humidity module
This is my first Python program. I've written it as part of a personal project to expand my skills & knowledge.

The aim of this component is to capture changes in temperature and humidity then publish the results to an Azure Event Grid.

This has been written for Python 3.

## Prerequisites
The following Python packages will be required.

- pip3 install azure-eventGrid
- pip3 install azure-mgmt-eventgrid
- pip3 install RPi.GPIO
- pip3 install-Adafruit-Blinka

## Running

Create a copy of the config file and add your own settings. The file name is required when running the code.

Arguments:
- -s or --sensor | accepts 1 or 2
- -c or --config | full filename of your config file

python3 DHTxx.py -s 1 -c prodconfig.json




### Some random notes:

The code has been written to target the DHT22 and DHT11 temperature sensors. 

Only a temperature or humdity changes more than a relative variance are published. This is controlled by a constant on in the sensors code.

