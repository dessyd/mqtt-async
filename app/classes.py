import logging
import socket
import time
from configparser import ConfigParser
from dataclasses import dataclass, field


@dataclass
class NetObject:
    host: str = field(default="localhost")

    def config(self, config_file="mqtt.conf") -> None:
        """Configure vars from corresponding stanza in config_file"""

        _stanza = self.__class__.__name__
        try:
            _config = ConfigParser()
            _config.read(config_file)

            for _var in _config[_stanza]:
                setattr(self, _var, _config.get(_stanza, _var))

        except Exception as _e:
            logging.warning(f"file {config_file} error: {_e}")

        # Convert initialized value back to <int> instead of <str>
        _port = int(self.port)
        self.port = _port


@dataclass
class Broker(NetObject):
    """Broker holds a MQTT Broker connection
    so it needs a topic to subscribe to"""

    port: int = field(default=1883)
    topic: str = field(default="Things/#")


@dataclass
class HecAPI(NetObject):
    """HecAPI holds a Splunk HEC connection"""

    port: int = field(default=8088)
    token: str = field(default="00000000-0000-0000-0000-000000000000")

    def url(self) -> str:
        return f"https://{self.host}:{self.port}/services/collector"

    def authHeader(self):
        return {"Authorization": f"Splunk {self.token}"}


@dataclass
class Metric:
    """Metric holds the typical payload for sending metrics via HEC"""

    topic: str = field(default="Things/#")
    payload: str = field(default="0.0")
    sourcetype: str = field(default="mqtt_metric")

    def post_data(self):
        """Create JSON expected by Splunk HEC for metrics
        The expected topic structure is the following
        /Things/<board_id>/<sensor_type>/<metric_name>
        payload holding the <metric_value>
        """
        _sub_topics = self.topic.rsplit("/", 3)
        fields = {}
        fields.update({"board_id": _sub_topics[-3]})
        fields.update({"sensor_type": _sub_topics[-2]})
        fields.update({"metric_name:" + _sub_topics[-1]: self.payload})

        post_data = {}
        post_data.update({"time": time.time()})
        post_data.update({"host": socket.gethostname()})
        post_data.update({"event": "metric"})
        post_data.update({"source": "metrics"})
        post_data.update({"sourcetype": self.sourcetype})
        post_data.update({"fields": fields})

        return post_data
