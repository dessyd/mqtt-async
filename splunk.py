from configparser import ConfigParser
import paho.mqtt.client as mqtt
import time, requests, socket
##turns off the warning that is generated below because using self signed ssl cert
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# All Classes defined here are a mirror of the config file stanzas
# Broker holds a MQTT Broker connection
class Broker:
    def __init__(self):
      self.host = "mqtt.eclipseprojects.io"
      self.port = 1883
      self.topic = "$SYS/#"

# Splunk holds a Splunk HEC connection
class Splunk:
    def __init__(self):
      self.host = "localhost"
      self.port = 8088
      self.token = "00000000-0000-0000-0000-000000000000"

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code %s" %rc)
   client.subscribe(broker.topic, qos=1)

def on_message(client, userdata, message):
   print("---")
   # Post received message to Splunk
   hec_post(message.topic, message.payload.decode())

def hec_post(topic, payload):
   post_status = False

   print("Topic: %s" %topic)
   print("Payload: %s" %payload)

   # Last sub topic is the measure name
   # Format it as a metric
   metric_name = "metric_name:"+topic.rsplit("/",1)[-1]
   # Payload being the measurement itself
   metric_data = {
      "topic": topic,
      metric_name: payload
   }
   # Format HEC event with metric
   post_data = {
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": "mqtt_metric",
      "fields": metric_data
   }

   # Create request URL  
   request_url = "https://%s:%s/services/collector" % (splunk.host, splunk.port)
   
   # Create auth header
   auth_header = "Splunk %s" % splunk.token
   authHeader = {'Authorization' : auth_header}

   try:
      r = requests.post(request_url, headers=authHeader, json=post_data, verify=False)
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

   # Get the MQTT Broker connection details.
   # 
   global broker
   broker = Broker()

   # Get the Splunk HEC details
   # Initialized once here
   # Used in the HEC post function
   global splunk 
   splunk = Splunk()

   # Initialize the connection details from the config file
   config = ConfigParser()
   config.read('mqtt.conf')

   # Each Class mirrors a stanza
   broker.host = config.get('Broker','host')
   broker.port = config.getint('Broker','port')
   broker.topic = config.get('Broker','topic')

   splunk.host = config.get('Splunk','host')
   splunk.port = config.getint('Splunk', 'port')
   splunk.token = config.get('Splunk','token')

   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message

   client.connect(broker.host, broker.port, 60)

   client.loop_forever()

main()