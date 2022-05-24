import paho.mqtt.client as mqtt
import time, random, schedule, uuid
from classes import Broker

config_file = 'mqtt.conf'
broker = Broker()
broker.config(config_file)
board_id = str(uuid.getnode())

def pub(client):
    Topic="Things/thing-%s/dht11-%i/air.humidity" % (board_id, random.randint(0,9))
    Payload=random.randint(0,10000)/100
    client.publish(topic=Topic, payload=Payload, qos=1, retain=False)

def conn(client):
    client.connect(broker.host, broker.port, 60)

def main():

    client = mqtt.Client()
    conn(client)
    schedule.every(60).seconds.do(conn, client)

    schedule.every(5).seconds.do(pub, client)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()