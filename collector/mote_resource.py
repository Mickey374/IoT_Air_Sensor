from coapthon.resources.resource import Resource
from coapthon.client.coap import CoAP
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
from database import Database
import server
import json
import threading
import time
import logging
import tabulate

class MoteResource:
    def __init__(self, source_address):
        self.db = Database
        self.connection = self.db.connect_db()
        self.actuator_resource = "LEDs"
        self.address = source_address
        self.resource = "aqi"
        self.aqi = 0
        self.ts = 0
    
    def execute_query(self):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `coap` (`aqi`, `timestamp`) VALUES (%s, %s)"
            cursor.execute(sql, (self.aqi, self.ts))
        self.connection.commit()
        self.show_log()
    
    def show_log(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `coap`"
            cursor.execute(sql)
            results = [x for x in cursor] 
            header = results[0].keys() if len(results) > 0 else []  
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows, header, tablefmt='grid'))
            
    def observe(self, response):
        print("Callback Initiated")

        if response.payload is None:
            print("No Response Received")
        else:
            print("Reponse: ", response.payload)
            node_data = json.loads(response.payload)
            
            if not node_data["aqi"]:
                print("Empty Values")
                return
            self.aqi = node_data["aqi"]
            self.ts = node_data["ts"]

            if self.aqi < 51:
                response = self.client.post(self.actuator_resource, "mode=good")
            elif self.aqi < 101:
                response = self.client.post(self.actuator_resource, "mode=moderate")
            else:
                response = self.client.post(self.actuator_resource, "mode=unhealthy")
    
    def start_observing(self):
        logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
        logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
        logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
        self.client = HelperClient(self.address)
        self.client.observe(self.resource, self.observer)