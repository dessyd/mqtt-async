import logging
import paho.mqtt.client as mqtt
import requests
from requests.exceptions import ConnectionError, HTTPError
from requests.packages import urllib3
from classes import Broker, HecAPI, Metric

log_level=logging.DEBUG
log_format='%(asctime)s %(message)s'
logging.basicConfig(level=log_level,format=log_format)

def on_connect(client, userdata, flags, rc):
   logging.info("Connected to MQTT With Result Code %s" %rc)
   client.subscribe(broker.topic, qos=1)

def on_message(client, userdata, message):
   hec_post(topic=message.topic, payload=message.payload.decode())

Status = bool
def hec_post(topic, payload) -> Status:
   """ Post received message to Splunk """
   urllib3.disable_warnings()

   post_status = False
   metric = Metric(topic, payload)

   logging.debug("Topic: %s" %topic)
   logging.debug("Payload: %s" %payload)

   try:
      r = requests.post(hec_api.url(), headers=hec_api.authHeader(), json=metric.post_data(), verify=False)
      r.raise_for_status()
   except ConnectionError as err: 
      print("Splunk refused connection: %s" %err)  
      return post_status
   except HTTPError as err:
      print("HTTP Error: %s" %err)
      return post_status
   
   logging.debug("Successful connection to Splunk")
   # Check Splunk return code
   try:
      text = r.json()["text"]
      code = r.json()["code"]
   except:
      print("No valid JSON returned from Splunk")
      return post_status

   if code != 0:
      raise Exception("Splunk error code %s" %code)
   else:
      logging.info("Splunk HEC POST %s" %text)
      post_status = True

   return post_status

def main():
   global broker
   global hec_api

   config_file = 'mqtt.conf'

   broker = Broker()
   broker.config(config_file)

   hec_api = HecAPI()
   hec_api.config(config_file)
         
   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message

   client.connect(broker.host, broker.port, 60)

   client.loop_forever()

if __name__ == "__main__":
    main()