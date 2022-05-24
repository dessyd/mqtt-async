from dataclasses import dataclass, field
import socket, time

# Classes defined here are a mirror of the config file stanzas

@dataclass
class Broker:
  """ Broker holds a MQTT Broker connection """
  host: str =field(default="mqtt.eclipseprojects.io")
  port: int =field(default=1883)
  topic: str =field(default="$SYS/#")

@dataclass
class HecAPI:
  """ HecAPI holds a Splunk HEC connection """
  host: str = field(default="localhost")
  port: int = field(default=8088)
  token: str = field(default="00000000-0000-0000-0000-000000000000")

  def url(self) -> str:
    return "https://%s:%s/services/collector" %(self.host, self.port)

  def authHeader(self) -> str:
    return {'Authorization' : "Splunk %s" % self.token}
    
@dataclass
class Metric:
  """ Metric holds the typical payload for sending metrics via HEC """
  topic: str = field(default="Things/#")
  payload: str = field(default="0.0")
  sourcetype: str = field(default="mqtt_metric")

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