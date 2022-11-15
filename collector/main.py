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
    "filter\n" \
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
    
    elif command == "logs":
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
    
    elif command == "activate":
        client.communicateToSensors("start", "inValues")

    elif command == "simulate":
        try:
            data = getValuesFromClient(client, client1)
            while True:
                # time.sleep(1)
                statFans = str(globalStatus.setFanStatus)
                statFilters = str(globalStatus.setFilterStatus)
                data = getValuesFromClient(client, client1)
                # >>Clear the terminal
                os.system('cls' if os.name == 'nt' else 'clear')
                print(pa.airSensor[statFans][statFilters].format(data[0],data[1],data[2],data[3],data[4]))
                print("\n>>Press Ctrl+C to exit\n")
                time.sleep(1)

        
        except KeyboardInterrupt:
            return
    
    elif command == "change param":
        globalStatus.changeVal = 1
        conf = start_configuration()

        client.tempMax = conf["tempMax"]
        client.tempMin = conf["tempMin"]
        client.humMax = conf["humMax"]
        client.humMin = conf["humMin"]
        client.co2Max = conf["co2Max"]
        client.co2Min = conf["co2Min"]
        globalStatus.changeVal = 0
    
    elif command == "exit":
        print("\n>>Shutting Down")
        os._exit(0)




def showInfo():
    return 1


def start_configuration():
    return 1