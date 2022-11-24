import paho.mqtt.client as mqtt
import json
from time import sleep
from datetime import datetime
from database.db import Database
from pydoc import cli
from coapNetwork.addresses import Addresses
from coapNetwork.sendPost import Post
from globalStatus import globalStatus

class MqttClientExtractionFilter:
    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("status_gasExtractor")
        self.client.subscribe("actuator__gasExtractor")