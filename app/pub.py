import random
import time
import uuid

import paho.mqtt.client as mqtt
import schedule

from classes import Broker

config_file = "mqtt.conf"
broker = Broker()
broker.config(config_file)
board_id = f"{uuid.getnode():x}"  # get rid of leading 0x


def pub(client):
    _sensor_number = random.randint(0, 9)
    _sensor_path = f"Things/{board_id}/dht11-{_sensor_number}/air."
    _sensors = ["temperature", "humidity", "pressure"]

    for _sensor_name in _sensors:
        _measure = random.randint(0, 10000) / 100
        client.publish(
            topic=f"{_sensor_path}{_sensor_name}", payload=_measure, qos=1, retain=False
        )


def conn(client):
    client.connect(broker.host, broker.port, 60)


def main():

    client = mqtt.Client()
    conn(client)
    schedule.every(60).seconds.do(conn, client)

    schedule.every(10).seconds.do(pub, client)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
