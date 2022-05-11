import time, socket

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

class Metric:
  def __init__(self, topic="Things/#", payload="0.00"):
    self.topic = topic
    self.payload = payload
  def post_data(self):
    return { 
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": "mqtt_metric",
      "fields": {"topic": self.topic, "metric_name:"+self.topic.rsplit("/",1)[-1]: self.payload}
      }
  def __str__(self):
    return str(self.__dict__)


def do_print():
    print(hec_api)
    print(hec_api.url())
    print(hec_api.authHeader())
    print(hec_metric.post_data())

def main():
    global hec_api, hec_metric
    hec_api = HecAPI("gurga", 2048)
    hec_api.port = 512
    hec_metric = Metric(payload="23.04", topic="Thing/servo2/uva_index")
    do_print()

main()


