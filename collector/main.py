import threading
import os
import json
import logging
import tabulate
import argparse
import paho.mqtt.client as mqtt
from datetime import datetime
from coapthon.server.coap import CoAP
from database import Database
from server import *

# Define Variables
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "info"
MQTT_MSG = "hello MQTT"

ip = "::"
port = 5683

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("registry", AdvancedResource())

class MqttClient():
    def on_connect(self, client, userdata, msg):
        self.client.subscribe(MQTT_TOPIC, 0)

    
    def on_message(self, client, userdata, msg):
        print("Payload: " + str(msg.payload))
        print("QOS: " + str(msg.qos))
        print("Topic: " + str(msg.topic))

        receivedData = json.loads(msg.payload)
        temperature = receivedData["temp"]
        humidity = receivedData["humidity"]
        light = receivedData["light"]
        gas = receivedData["gas"]

        if receivedData["light"] == 0:
            light = "INTENSE"
        elif receivedData["light"] == 1:
            light = "NORMAL"
        else:
            light = "DIM"
        
        dt = datetime.now()
        curr_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `mqttsensors`  (`temperature`, `humidity`, `light`, `gas`, `timestamp`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (temperature, humidity, light, gas, curr_dt))
        
        self.connection.commit()
        self.show_log
    
    def show_log(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `mqttsensors`"
            cursor.execute(sql)
            results = cursor.fetchall()
            header = results[0].keys() if len(results) > 0 else []  
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows, header, tablefmt='grid'))

logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)

#Initialize the MQTT Client
mqtt_cl = MqttClient()
mqtt_thread = threading.Thread(target=mqtt_cl.mqtt_client,args=(),kwargs={})
mqtt_thread.start()

server = CoAPServer(ip, port)
try:
    print("Listening to server")
    server.listen(100)
except KeyboardInterrupt:
    print("Server Shutdown")
    mqtt_cl.kill()
    mqtt_cl.join()
    server.close()
    print("Exiting!")

mqtt_cl.loop_forever()