from configparser import ConfigParser
import paho.mqtt.client as mqtt
import requests
##turns off the warning that is generated below because using self signed ssl cert
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from classes import Broker, HecAPI, Metric

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
      r = requests.post(hec_api.url(), headers=hec_api.authHeader(), json=metric.post_data(), verify=False)
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
   broker_stanza = "Broker"
   global broker
   broker = Broker(
      host=config.get(broker_stanza,'host'), 
      port=config.getint(broker_stanza,'port'),
      topic=config.get(broker_stanza,'topic')
      )

   # Get the Splunk HEC details
   # Initialized once here
   # Used in the HEC post function
   hec_stanza = "HecAPI"
   global hec_api
   hec_api = HecAPI(
      host=config.get(hec_stanza,'host'), 
      port=config.getint(hec_stanza,'port'), 
      token=config.get(hec_stanza,'token')
      )

   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message

   client.connect(broker.host, broker.port, 60)

   client.loop_forever()

if __name__ == "__main__":
    main()