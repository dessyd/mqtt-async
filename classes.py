import socket, time
import logging
from dataclasses import dataclass, field
from configparser import ConfigParser

@dataclass
class NetObject:
  host: str = field(default="localhost")
  port: int = field(default=8000)

  def config(self, config_file="default.conf") -> None:
    """ Configure vars from corresponding stanza in config_file """

    _stanza = self.__class__.__name__
    try:
      _config = ConfigParser()
      _config.read(config_file)

      for _var in self.__dict__ :
        setattr(self,_var,_config.get(_stanza,_var))
      _port = int(self.port)
      self.port = _port
    except Exception as _e:
      logging.ERROR(f'Config file {config_file} error: {_e}')

@dataclass
class Broker(NetObject):
  """ Broker holds a MQTT Broker connection 
      so it needs a topic to subscribe to """
  topic: str =field(default="$SYS/#")

@dataclass
class HecAPI(NetObject):
  """ HecAPI holds a Splunk HEC connection """
  token: str = field(default="00000000-0000-0000-0000-000000000000")

  def url(self) -> str:
    return f"https://{self.host}:{self.port}/services/collector"

  def authHeader(self):
    return {'Authorization' : f'Splunk {self.token}'}

@dataclass
class Metric:
  """ Metric holds the typical payload for sending metrics via HEC """
  topic: str = field(default="Things/#")
  payload: str = field(default="0.0")
  sourcetype: str = field(default="mqtt_metric")

  def post_data(self):
    """ Create JSON expected by Splunk HEC for metrics """
    return { 
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": self.sourcetype,
      # Latest subtopic is considered to be the measurement name
      # payload being the measured value
      "fields": {"topic": self.topic, 
               "metric_name:"+self.topic.rsplit("/",1)[-1]: self.payload
               }
      }