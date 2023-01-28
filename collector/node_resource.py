import getopt
import json
import threading
import time
import logging
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
from server import *
from database import Database
import tabulate
from datetime import datetime

class NodeResource:
    def __init__(self, source_address):
         #Initialize the fields for the mote resource
        self.db = Database()
        self.connection = self.db.connect_db()
        self.actuator_resource = "LEDs"
        self.address = source_address
        self.resource = "aqi"
        self.airquality = 10
        self.currt = 0
    
    def execute_query(self):
        with self.connection.cursor() as cursor:
            dt = datetime.now()
            curr_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO `coap`  (`aqi`, `timestamp`) VALUES (%s, %s)"
            cursor.execute(sql, (self.airquality, curr_dt))
        self.connection.commit()

        with self.connection.cursor() as new_cursor:
            sql = "SELECT * FROM `coap`"
            new_cursor.execute(sql)
            results = new_cursor.fetchall()
            header = results[0].keys() if len(results) > 0 else []  
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows, header, tablefmt='grid'))

    def observer(self, response):
        print("Callback Initiated, Resource arrived")
        if response.payload is None:
            print("No Response Received")

        if response.payload is not None:
            print("Response")
            print(response.payload)

            #Read the data
            node_data = json.loads(response.payload)

            #Check if the object aqi exists
            if node_data["aqi"] is None or node_data["aqi"] == "":
                print("Empty payload")
                return
            self.airquality = int(node_data["aqi"])
            self.currt = int(node_data["timestamp"])
            

            #When the Air Quality is beyond a threshold
            if self.airquality <= 50:
                response = self.client.post(self.actuator_resource, "mode=safe")
            elif 50 < self.airquality < 120:
                response = self.client.post(self.actuator_resource, "mode=normal")
            elif self.airquality > 120:
                response = self.client.post(self.actuator_resource, "mode=toxic")
            self.execute_query()
    
    def start_observing(self):
        logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
        logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
        logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
        self.client = HelperClient(self.address)
        self.client.observe(self.resource, self.observer)