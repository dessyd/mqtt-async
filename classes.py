import socket, time
from dataclasses import dataclass, field
from configparser import ConfigParser

# Classes defined here are a mirror of the config file stanzas

@dataclass
class Broker:
  """ Broker holds a MQTT Broker connection """
  host: str =field(default="mqtt.eclipseprojects.io")
  port: int =field(default=1883)
  topic: str =field(default="$SYS/#")

  def config(self, config_file: str) -> None:
    """ Configure from stanza in config file """
    try:
      _config = ConfigParser()
      _config.read(config_file)

      _stanza = self.__class__.__name__
      self.host=_config.get(_stanza,'host')
      self.port=_config.getint(_stanza,'port')
      self.topic=_config.get(_stanza,'topic')
    except Exception as _e:
      print('Bad config file ' + config_file + ': ' + str(_e))

@dataclass
class HecAPI:
  """ HecAPI holds a Splunk HEC connection """
  host: str = field(default="localhost")
  port: int = field(default=8088)
  token: str = field(default="00000000-0000-0000-0000-000000000000")

  def config(self, config_file: str) -> None:
    """ Configure from stanza in config file """
    try:
      _config = ConfigParser()
      _config.read(config_file)

      _stanza = self.__class__.__name__
      self.host=_config.get(_stanza,'host')
      self.port=_config.getint(_stanza,'port')
      self.token=_config.get(_stanza,'token')
    except Exception as _e:
      print('Bad config file ' + config_file + ': ' + str(_e))

  def url(self) -> str:
    return "https://%s:%s/services/collector" %(self.host, self.port)

  def authHeader(self):
    return {'Authorization' : "Splunk %s" % self.token}

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