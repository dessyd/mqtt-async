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
   hec_post(message.topic, message.payload.decode())

def hec_post(topic, payload):

   print("Topic: %s" %topic)
   print("Payload: %s" %payload)
   print("---")

   # Last sub topic is the measure name
   # payload being the measrement itself
   metric_name = "metric_name:"+topic.rsplit("/",1)[-1]
   metric_data = {
      "topic": topic,
      metric_name: payload
   }
   
   post_data = {
      "time": time.time(), 
      "host": socket.gethostname(),
      "event": "metric",
      "source": "metrics",
      "sourcetype": "mqtt",
      "fields": metric_data
   }
   
   print(post_data)

   # Create request URL
   request_url = "https://%s:%s/services/collector" % (splunk.host, splunk.port)
   
   # Create auth header
   auth_header = "Splunk %s" % splunk.token
   authHeader = {'Authorization' : auth_header}

   # Create request
   post_success = False

   try:

      r = requests.post(request_url, headers=authHeader, json=post_data, verify=False)
      try:
         r.raise_for_status()
      except requests.exceptions.HTTPError as e:
         # Whoops it wasn't a 200
         print("Error: " + str(e))
         return post_success

      # Must have been a 200 status code
      print(r.json())

   except Exception as err:
      # Network or connection error
      print ("Error sending request " + str(err))

   return post_success

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