import logging
import os
import sys

import paho.mqtt.client as mqtt
import requests
from classes import Broker, HecAPI, Metric
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError
from requests.packages import urllib3

log_level = logging.DEBUG
log_format = "%(asctime)s %(levelname)s %(funcName)s %(message)s"
logging.basicConfig(level=log_level, format=log_format)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT With Result Code {rc}")
        client.subscribe(broker.topic, qos=1)


def on_message(client, userdata, message):
    hec_post(topic=message.topic, payload=message.payload.decode())


Status = bool


def hec_post(topic, payload) -> Status:
    """Post received messqage to Splunk

    Transfer the payload received to Splunk using HTTP Event Collector

    Args:
        topic (str): The full topic path subscribed
        patload (str): the measured value

    Returns:
       Status: bool the execution status of the POST
    """
    urllib3.disable_warnings()

    post_status = False
    metric = Metric(topic, payload)

    logging.info(f"Topic: {metric.topic}")
    logging.info(f"Payload: {metric.payload}")
    logging.info(f"SourceType: {metric.sourcetype}")

    try:
        r = requests.post(
            hec_api.url(),
            headers=hec_api.authHeader(),
            json=metric.post_data(),
            verify=False,
        )
        r.raise_for_status()
    except ConnectionError as _err:
        logging.error(f"Splunk refused connection: {_err}")
        return post_status
    except HTTPError as _err:
        logging.error(f"HTTP Error: {_err}")
        return post_status
    except Exception as _err:
        logging.error(_err)
        return post_status

    logging.debug("Successful connection to Splunk")
    # Check Splunk return code
    try:
        text = r.json()["text"]
        code = r.json()["code"]
    except Exception as err:
        logging.error(f"No valid JSON returned from Splunk; {err}")
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

    try:
        logging.debug(f"Connecting to {broker.host}:{broker.port}")
        client.connect(broker.host, broker.port, 60)
    except Exception as _err:
        logging.error(f"Connection to {broker.host}:{broker.port} failed: {_err}")
        sys.exit(1)

    client.loop_forever()


if __name__ == "__main__":
    main()
