import logging
import os

import paho.mqtt.client as mqtt
import requests
from classes import Broker, HecAPI, Metric
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError
from requests.packages import urllib3

log_level = logging.INFO
log_format = "%(asctime)s %(levelname)s %(funcName)s %(message)s"
logging.basicConfig(level=log_level, format=log_format)


def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT With Result Code {rc}")
    client.subscribe(broker.topic, qos=1)


def on_message(client, userdata, message):
    hec_post(topic=message.topic, payload=message.payload.decode())


Status = bool


def hec_post(topic, payload) -> Status:
    """Post received message to Splunk"""
    urllib3.disable_warnings()

    post_status = False
    metric = Metric(topic, payload)

    logging.info(f"Topic: {topic}")
    logging.info(f"Payload: {payload}")

    try:
        r = requests.post(
            hec_api.url(),
            headers=hec_api.authHeader(),
            json=metric.post_data(),
            verify=False,
        )
        r.raise_for_status()
    except ConnectionError as err:
        logging.error(f"Splunk refused connection: {err}")
        return post_status
    except HTTPError as err:
        logging.error(f"HTTP Error: {err}")
        return post_status

    logging.debug("Successful connection to Splunk")
    # Check Splunk return code
    try:
        text = r.json()["text"]
        code = r.json()["code"]
    except:
        logging.error("No valid JSON returned from Splunk")
        return post_status

    if code != 0:
        raise Exception(f"Splunk error code: {code}")
    else:
        logging.info(f"Splunk HEC POST: {text}")
        post_status = True

    return post_status


def main():
    global broker
    global hec_api

    load_dotenv()  # take environment variables from .env.
    config_file = os.getenv("CONFIG_FILE")

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
