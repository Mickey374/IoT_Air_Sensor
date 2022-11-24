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
        self.client.subscribe("actuator_gasExtractor")
    
    def update_gas_monitoring_status(self, ad, status):
        dt = datetime.now()
        cursor = self.connection.cursor()
        query = "INSERT INTO `actuator_filtering` (`address`, `timestamp`, `status`) VALUES (%s, %s, %s)"
        cursor.execute(query, (str(ad), dt, status))
        print("\nSTATUS = "+ status)
        self.connection.commit()
    
