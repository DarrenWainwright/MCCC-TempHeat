class Sensor(object):
    

    @staticmethod
    def GetDetails(self, retries):
        if retries == 0:
            return "Could not retrieve"
        try:
            details = {}
            details.temperature_c = self.temperature
            details.temperature_f = self.temperature_c * (9 / 5) + 32
            details.humidity = self.humidity
            return details
        except Exception:
            r = retries-1
            return Sensor.GetDetails(self, r)
        