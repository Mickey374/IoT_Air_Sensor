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


class AlertResource:
    def __init__(self, resource, source_address):
        #Initialize the fields for the mote resource
        self.db = Database()
        self.connection = self.db.connect_db()
        self.actuator_resource = "alert_actuator"
        self.resource = resource
        self.address = source_address
        self.intensity = 15
        self.isActive = "F"

        #Start Observing the Resource from the Source address
        self.start_observing()
        print("Resource Observing Init...")
    
    def observer(self, response):
        print("Callback Initiated")
        if response.payload is None:
            print("No Response Received")
        else:
            print("Response", response.payload)

            #Read the data
            node_data = json.loads(response.payload)
            info = node_data["info"].split(" ")
            intensity = node_data["intensity"].split(" ")
            print("Current extraction value: \n")
            print(info, intensity)

            self.isDetected = info[0]
            self.intensity = intensity[0]

            #When the poisonous gas is detected, initiate a query
            if self.isDetected == "T":
                print("Poisonous Gas detected")
                self.execute_query(1)
            else:
                print("Air Safe")
                self.execute_query(0)

    def execute_query(self, state):
        with self.connection.cursor() as cursor:
            dt = datetime.now()
            intensity = str(self.intensity)
            sql = "INSERT INTO `coapsensorextractor` (`state`, `intensity`, datetime) VALUES (%s, %s, %s)"
            cursor.execute(sql, (state, intensity, dt))
        self.connection.commit()
        self.show_log()
        
    def show_log(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `coapsensorextractor`"
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