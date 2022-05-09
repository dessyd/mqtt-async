import paho.mqtt.client as mqtt
from configparser import ConfigParser

config = ConfigParser()
config.read('mqtt.conf')
broker_host = config.get('Broker','host')
broker_port = config.getint('Broker','port')
broker_topic = config.get('Broker','topic')

def on_connect(client, userdata, flags, rc):
 print("Connected With Result Code "+str(rc))
 client.subscribe(broker_topic, qos=1)

def on_message(client, userdata, message):
    print("Topic: "+message.topic)
    print("Payload: "+message.payload.decode())
    print("---")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_host, broker_port, 60)


# client.publish(topic="TestingTopic", payload="TestingPayload", qos=1, retain=False)
client.loop_forever()
