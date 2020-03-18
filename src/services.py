import time
import uuid
import json
from datetime import datetime
from azure.eventgrid import EventGridClient
from msrest.authentication import TopicCredentials

class Sensor(object):

    # Sensor details to return
    class SensorDetail(object):
        def __init__(self, temperature_in_c, humidity):          
            self._temperature_c = temperature_in_c
            self._humidity = humidity
        
        def Temperature_C(self):
            return self._temperature_c
   
        def Temperature_F(self):
            if self._temperature_c is None:
                return None
            return self._temperature_c * (9 / 5) + 32

        def Humidity(self):
            return self._humidity


    # PArse the details from the sensor instance
    @staticmethod
    def GetDHTxxDetails(sensorInstance, retries): 
        if retries == 0:
            return Sensor.SensorDetail(None,None)
        try:
            time.sleep(2)
            return Sensor.SensorDetail(sensorInstance.temperature, sensorInstance.humidity)           
        except Exception:
            r = retries-1
            return Sensor.GetDHTxxDetails(sensorInstance, r)
        

class EventGrid(object):

    @staticmethod
    def PublishEvent(endpoint, subject, eventType, dataJson):
        try:
            credentials = TopicCredentials(
            #TODO - get a key..
            self.settings.EVENT_GRID_KEY
            )
            event_grid_client = EventGridClient(credentials)
            event_grid_client.publish_events(
                endpoint,
                events=[{
                    'id' : uuid.uuid4(),
                    'subject' : subject,
                    'data': json.dumps(dataJson),
                    'event_type': eventType,
                    'event_time': datetime.utcnow(),
                    'data_version': 1
                }]
            )
        except:
            pass
        