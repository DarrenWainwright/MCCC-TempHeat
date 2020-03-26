import time, uuid, json
from datetime import datetime

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import Topic

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

    class MCCCTopic(object):
        def __init__(self, topic, key, endpoint):
            print(f"MCCC Topic. Name: {topic}, Key:{key}, Endpoint:{endpoint}")
            self._name = topic
            self._key = key
            self._endpoint = endpoint

        def Name(self):
            return self._name
        def Key(self):
            return self._key
        def Endpoint(self):
            return self._endpoint
        

    @staticmethod
    #Returns dictionary of topicName/key
    def CreateOrUpdateTopics(mgmtJson):

        subscription_id = f"{mgmtJson['subscriptionId']}"

        credentials = ServicePrincipalCredentials(
            client_id=mgmtJson["azureClientId"],
            secret=mgmtJson["azureClientSecret"],
            tenant=mgmtJson["azureTenantId"]
            )

        event_grid_client = EventGridManagementClient(credentials, subscription_id)
        
        returnDict = {}
        for topic in mgmtJson["topicNames"]:
            print(f'Create Event Grid Topic {topic}')
            topic_result_poller = event_grid_client.topics.create_or_update(mgmtJson["resourceGroupName"],
                                                                     topic,
                                                                     Topic(
                                                                         location=mgmtJson["location"],
                                                                         tags={'createdBy': 'MCCC'}
                                                                     ))
            # Blocking call            
            topic_result = topic_result_poller.result()  # type: Topic
            print(topic_result)
            print(f"Topic {topic} Created ")
            keys = event_grid_client.topics.list_shared_access_keys(
                        mgmtJson["resourceGroupName"],
                        topic
                    )             
            rTopic = EventGrid.MCCCTopic(topic, keys.key1, topic_result.endpoint)

            returnDict[topic] = rTopic

        return returnDict
            

    @staticmethod
    def PublishEvent(endpoint, key, subject, eventType, dataJson):
        try:
            credentials = TopicCredentials(key)
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
        