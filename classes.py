import socket, time

# Classes defined here are a mirror of the config file stanzas
# Broker holds a MQTT Broker connection
class Broker:
   def __init__(self, host="mqtt.eclipseprojects.io", port=1883, topic="$SYS/#"):
      self.host = host
      self.port = port
      self.topic = topic
   def __str__(self):
      return str(self.__dict__)

# HecAPI holds a Splunk HEC connection
class HecAPI:
  def __init__(self, host="localhost", port=8088, token="00000000-0000-0000-0000-000000000000"):
    self.host = host
    self.port = port
    self.token = token
  def url(self):
    return "https://%s:%s/services/collector" %(self.host, self.port)
  def authHeader(self):
    return {'Authorization' : "Splunk %s" % self.token}
  def __str__(self):
      return str(self.__dict__)

# Metric holds the typical payload for sending metrics via HEC
class Metric:
  def __init__(self, topic="Things/#", payload="0.00", sourcetype="mqtt_metric"):
    self.topic = topic
    self.payload = payload
    self.sourcetype = sourcetype
  def post_data(self):
    return { 
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": self.sourcetype,
      "fields": {"topic": self.topic, 
               "metric_name:"+self.topic.rsplit("/",1)[-1]: self.payload
               }
      }
  def __str__(self):
    return str(self.__dict__)