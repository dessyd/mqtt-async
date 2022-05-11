import time, socket
class Person:
    def __init__(self, name="Peter", age=20):
        self.name = name
        self.age = age
        self.mix = "Mix of %s and %s" %(name, age)

    def __str__(self):
        return str(self.__dict__)
global p1, p2

class Splunk:
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
    self.post_data = { 
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": "mqtt_metric",
      "fields": {"topic": topic, "metric_name:"+topic.rsplit("/",1)[-1]: payload}
      }
  def __str__(self):
    return str(self.__dict__)


def do_print():
    print(splunk)
    print(splunk.url())
    print(splunk.authHeader())
    # print(hec_metric.post_data)

def main():
    global splunk, hec_metric
    splunk = Splunk("gurga", 2048)
    splunk.port = 512
    # hec_metric = Metric(payload="18.04")
    do_print()
    # hec_metric = Metric(payload="23.04", topic="Thing/servo2/uva_index")
    # do_print()

main()


