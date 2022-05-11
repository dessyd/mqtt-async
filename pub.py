# from multiprocessing.connection import Client
import paho.mqtt.client as mqtt
import time, random, schedule

from configparser import ConfigParser

config = ConfigParser()
config.read('mqtt.conf')
broker_host = config.get('Broker','host')
broker_port = config.getint('Broker','port')

def pub(client):
    Topic="Things/thing%i/sensor%i/air.temperature" % (random.randint(1000,9999), random.randint(0,9))
    Payload=random.randint(0,10000)/100
    client.publish(topic=Topic, payload=Payload, qos=1, retain=False)

def conn(client):
    client.connect(broker_host, broker_port, 60)

def main():
    client = mqtt.Client()
    client.connect(broker_host, broker_port, 60)
    schedule.every(60).seconds.do(conn, client)

    schedule.every(5).seconds.do(pub, client)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()