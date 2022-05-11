from configparser import ConfigParser
import paho.mqtt.client as mqtt
import time, requests, socket
##turns off the warning that is generated below because using self signed ssl cert
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# All Classes defined here are a mirror of the config file stanzas
# Broker holds a MQTT Broker connection
class Broker:
   def __init__(self, host="mqtt.eclipseprojects.io", port=1883, topic="$SYS/#"):
      self.host = host
      self.port = port
      self.topic = topic
   def __str__(self):
      return str(self.__dict__)

# Splunk holds a Splunk HEC connection
class Splunk:
   def __init__(self, host="localhost", port=8088, token="00000000-0000-0000-0000-000000000000"):
      self.host = host
      self.port = port
      self.token = token
      self.url = "https://%s:%s/services/collector" %(host, port)
      self.authHeader = {'Authorization' : "Splunk %s" % token}
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

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code %s" %rc)
   client.subscribe(broker.topic, qos=1)

def on_message(client, userdata, message):
   print("---")
   # Post received message to Splunk
   hec_post(topic=message.topic, payload=message.payload.decode())

def hec_post(topic, payload):
   print("Topic: %s" %topic)
   print("Payload: %s" %payload)
   
   post_status = False
   metric = Metric(topic, payload)

   try:
      r = requests.post(splunk.url, headers=splunk.authHeader, json=metric.post_data, verify=False)
      r.raise_for_status()
   except requests.exceptions.ConnectionError as err: 
      print("Splunk refused connection: %s" %err)  
      return post_status
   except requests.exceptions.HTTPError as err:
      # catastrophic error. bail.
      print("Exception %s" %err)
      return post_status
   
   # Connection is successful
   # Check Splunk return code
   try:
      text = r.json()["text"]
      code = r.json()["code"]
   except:
      print("No valid JSON returned from Splunk")
      return post_status

   if code != 0:
      print("Splunk error code %s" %code)
   else:
      print(text)
      post_status = True

   return post_status

def main():

   # Initialize the connection details from the config file``
   # Each Class mirrors a stanza
   config = ConfigParser()
   config.read('mqtt.conf')

   # Get the MQTT Broker connection details.
   # 
   global broker
   broker = Broker(
      host=config.get('Broker','host'), 
      port=config.getint('Broker','port'),
      topic=config.get('Broker','topic')
      )

   # Get the Splunk HEC details
   # Initialized once here
   # Used in the HEC post function
   global splunk
   splunk = Splunk(
      host=config.get('Splunk','host'), 
      port=config.getint('Splunk','port'), 
      token=config.get('Splunk','token')
      )

   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message

   client.connect(broker.host, broker.port, 60)

   client.loop_forever()

main()