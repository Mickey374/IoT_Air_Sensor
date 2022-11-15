import json
from pydoc import cli
import threading
import time
import os
import pixelart as pa
from coapNetwork.addresses import Addresses
from coapNetwork.sensor import ObserveSensor
from mqttNetwork.value_collector import MqttClientData
import paho.mqtt.client as mqtt
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.client.helperclient import HelperClient
from coapNetwork.resExample import ResExample
from globalStatus import globalStatus

ip = "::"
port = 5683

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("registry", ResExample())
    
    def allCommands():
        print(">> ALL COMMANDS TO START \n")
        print(
        "help \n"\
        "activate\n"\
        "logs\n"\
        "simulate\n"\
        "change params\n"
        "exit\n\n")
    
    def getValuesFromClient(client, client1):
        level = client1.levIn if client1.levIn else 50
        humidity = client.humIn if client.humIn else 60
        temperature = client.tempIn if client.tempIn else 27
        co2 = client.co2In if client.co2In else 1300
        tempOut = client.tempOut if client.tempOut else 30

        return [level, humidity, temperature, co2, tempOut]

    def checkUserCommand(command, client, client1):
        if command == "help":
            showInfo()
        
        elif command == "log":
            try:
                msg = str(client.message)
                print("\n>>Press Ctrl+C to terminate session \n")
                while True:
                    time.sleep(1)
                    if(str(client.message) != msg):
                        print("\n>>"+str(client.message)+ str(client1.message))
                        msg = str(client.message)
            except KeyboardInterrupt:
                return

        elif command == "filter":
            try:
                msg = str(client.message)
                print("\n>>Press Ctrl+C to terminate session \n")
                while True:
                    time.sleep(1)
                    if(str(client1.message) != msg):
                        print("\n>>"+str(client1.message))
                        msg = str(client1.message)
            except KeyboardInterrupt:
                return   
        
        




    