import time
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
        