import time, uuid, json
from datetime import datetime

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import Topic

from azure.eventgrid import EventGridClient
from msrest.authentication import TopicCredentials
from azure.eventgrid.models import EventGridEvent


#import logging
#logging.basicConfig(level=logging.DEBUG)

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
    # Fetches Event Grid Topic info. 
    # If the topics do not exist they will be created
    def GetEventGridTopics(tenantId, subscriptionId, resourceGroup, gridLocation, clientId, cientSecret, topicNames):

        credentials = ServicePrincipalCredentials(
            client_id=clientId,
            secret=cientSecret,
            tenant=tenantId
            )

        event_grid_client = EventGridManagementClient(credentials, subscriptionId)
        
        # list of current topics for this RG
        pagedTopics = event_grid_client.topics.list_by_resource_group(resourceGroup)

        returnDict = {}
        for topic in topicNames:
            print(f"Checking for existence of topic {topic}")
            p_topic = None 
            for paged_topic in pagedTopics:
                if topic == paged_topic.name:
                    p_topic = paged_topic
                    break        
            
            if p_topic == None:
                print(f"Topic {topic} does not exist. Creating now...")                
                topic_result_poller = event_grid_client.topics.create_or_update(resourceGroup,
                                                                        topic,
                                                                        Topic(
                                                                            location=gridLocation,
                                                                            tags={'createdBy': 'MCCC'}
                                                                        ))
                # Blocking call            
                topic_result = topic_result_poller.result()  # type: Topic
                print(topic_result)
                print(f"Topic {topic} Created ")                
            else:
                print(f"Topic {topic} already exists.")
            
            key = event_grid_client.topics.list_shared_access_keys(resourceGroup,topic).key1   
            endpoint = f"{topic}.{gridLocation}-1.eventgrid.azure.net"
            key = event_grid_client.topics.list_shared_access_keys(resourceGroup,topic).key1             
            rTopic = EventGrid.MCCCTopic(topic, key, endpoint)
            returnDict[topic] = rTopic

        return returnDict
            

    @staticmethod
    def PublishEvent(endpoint, key, subject, eventType, dataJson):
        try:
            events = []
            for i in range(1):
                events.append(EventGridEvent(
                    id=uuid.uuid4(),
                    subject=subject,
                    data=dataJson,
                    event_type=eventType,
                    event_time=datetime.utcnow(),
                    data_version=1.0
                ))

            credentials = TopicCredentials(key)
            event_grid_client = EventGridClient(credentials)
            event_grid_client.publish_events(
                endpoint,
                events=events
            )
            print("Published event") 
        except Exception as ex:
            print(ex)
            #TODO/ deal with this....
            pass
        