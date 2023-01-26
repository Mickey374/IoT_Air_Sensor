import tabulate
import json
import logging
import threading
import server
from database import Database
from datetime import datetime
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon import defines
from alert_resource import AlertResource


class PoisonResource:
    def __init__(self, resource, source_address):
        #Initialize the fields for the mote resource
        self.db = Database()
        self.connection = self.db.connect_db()
        self.address = source_address
        self.resource = resource
        self.actuator_resource = "alert_actuator"
        self.isDetected = "F"
        self.intensity = 15
        self.isActive = "F"

        #Start Observing the Resource from the Source address
        self.start_observing()
        print("Poison Air Resource Observing Init...")
    
    def observer(self, response):
        print("Callback Initiated Gas")
        if response.payload is None:
            print("No Response Received")
            return
        else:
            print("Response", response.payload)

            #Read the data
            node_data = json.loads(response.payload)
            isDetected = node_data["isDetected"].split(" ")
            info = node_data["info"].split(" ")
            intensity = node_data["intensity"].split(" ")
            print("Poisonous Gas value: \n")
            print(isDetected, info, intensity)
            self.isDetected = isDetected[0]
            self.intensity = intensity[0]
            self.isActive = info[0]

            #When the poisonous gas is detected, initiate a query
            if self.isDetected == "T":
                resp = self.client.post(self.actuator_resource, "state=1")
                print("Client response sent 1")
                self.execute_query_poisongas(1)
                
            else:
                resp = self.client.post(self.actuator_resource, "state=0")
                print("Client response sent 0")
                self.execute_query_poisongas(0)

    def execute_query_poisongas(self, state):
        with self.connection.cursor() as cursor:
            dt = datetime.now()
            intensity = str(self.intensity)
            extractor = str(self.isActive)
            sql = "INSERT INTO `coapsensorgas` (`state`, `extractor`, `intensity`, datetime) VALUES (%s, %s, %s,%s)"
            cursor.execute(sql, (state,extractor,intensity,dt))
        self.connection.commit()
        self.show_log()
        
    def show_log(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `coapsensorgas`"
            cursor.execute(sql)
            results = cursor.fetchall()
            header = results[0].keys() if len(results) > 0 else []  
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows, header, tablefmt='grid'))


    def start_observing(self):
        logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
        logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
        logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
        self.client = HelperClient(self.address)
        self.client.observe(self.resource, self.observer)
