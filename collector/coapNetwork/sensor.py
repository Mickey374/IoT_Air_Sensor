import json
from time import time
from datetime import datetime
from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.resources.resource import Resource
from coapthon.utils import parse_uri
from mqttNetwork.value_collector import MqttClientProfile
from database.db import Database
from globalStatus import globalStatus

class ObserveSensor:

    def __init__(self, resource, source_address, type):
        self.db = Database()
        self.connection = self.db.connect()
        self.address = source_address
        self.resource = resource
        self.type = type
        self.mqtt = None
        self.startObserving()
    

    def startObserving(self):
        self.client = HelperClient(self.address)
        self.mqtt = MqttClientProfile()
        self.mqtt.mqtt_client(None, None, None, None, None, None, "communicate")
        self.client.observe(self.resource, self.observer)
    
    def executeQuery(self, add, stat, timestamp, table):
        with self.connection.cursor() as cursor:
            cursor = self.connection.cursor()
            query = "INSERT INTO actuator_"+ table + "(`address`, `timestamp`, `status`, `manual`) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (str(add), timestamp, stat, "1"))
            self.connection.commit()

    def observer(self, response):
        data = json.loads(response.payload)
        
        #If the type is 0
        if self.type == 0:
            status = data["status"]
            dt = datetime.now()
            self.executeQuery(self.address, status, dt, "filtering")

            if str(status) == "1":
                if globalStatus.changeVal == 0: print("\n ☢️☢️ STARTING FILTERING PROCESS. ☢️☢️")
                globalStatus.setFilterStatus(1)
                self.mqtt.communicateToSensors(status, "filter")

            elif str(status) == "0":
                if globalStatus.changeVal == 0: print("\n DEFAULT STATE:: WAITING")
                globalStatus.changeVal(0)
                self.mqtt.communicateToSensors(status, "filter")
            

        #If the type is 1
        elif self.type == 1:
            status = data["open"]
            dt = datetime.now()
            self.executeQuery(self.address, status, dt, "fan")

            if str(status) == "1":
                if globalStatus.changeVal == 0: print("\n ☢️☢️ STARTING FAN")
                globalStatus.setFilterStatus(1)
                self.mqtt.communicateToSensors(status, "fan")

            elif str(status) == "0":
                if globalStatus.changeVal == 0: print("\n DEFAULT STATE:: WAITING")
                globalStatus.changeVal(0)
                self.mqtt.communicateToSensors(status, "fan")
