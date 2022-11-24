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
    
    def update_gas_monitoring_mode(self, node_id, mode):
        dt = datetime.now()
        cursor = self.connection.cursor()
        query = "INSERT INTO `gas_extractor` (`node_id`, `timestamp`, `mode`) VALUES (%s, %s, %s)"
        cursor.execute(query, (str(node_id), dt, mode))
        self.connection.commit()

    #This will be the callback for when a publish message is received from server
    def on_message(self, client, userdata, msg):
        #check the type of message received
        if(msg.topic == "status_gasExtractor"):
            self.message = msg.payload
            data = json.loads(msg.payload)
            node_id = data["node"]
            level = data["level"]
            self.levIn = level
            self.update_gas_monitoring_mode(node_id, level)
            self.checkActuatorMode(level)
        else:
            return
