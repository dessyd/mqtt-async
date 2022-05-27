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

    except Exception as _e:
      logging.warning(f'file {config_file} error: {_e}')

    # Convert initialized value back to <int> instead of <str>
    _port = int(self.port)
    self.port = _port

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
    """ Create JSON expected by Splunk HEC for metrics 
    The expected topic structure is the following
    /Things/<board_id>/<sensor_type>/<metric_name>
    payload holding the <metric_value> 
    """
    _sub_topics = self.topic.rsplit("/",3)
    return { 
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": self.sourcetype,
      "fields": {
        "board_id": _sub_topics[-3],
        "sensor_type": _sub_topics[-2],
        "metric_name:"+_sub_topics[-1]: self.payload
        }
      }