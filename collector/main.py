import json
from pydoc import cli
import threading
import time
import os
import pixelart as pa
import paho.mqtt.client as mqtt
from coapNetwork.addresses import Addresses
from coapNetwork.sensor import ObserveSensor
from mqttNetwork.value_collector import MqttClientData
from mqttNetwork.filter_extractor import MqttClientExtractionFilter
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
    humidity = client.humIn if client.humIn else 50
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

    else:
        print("/n>>Retry Commands Again...")
        allCommands()


def showInfo():
        print("\n"\
            ">>logs: Displays messages that the sensors delivers to the app \n"\
            ">>change params: Alters the current values of the threshold\n"\
            ">>filter: Check current state of Filters\n"\
            ">>simulate: Simulate the house sensor\n"\
            ">>activate: Starts all the sensors in the Network\n"
            ">>help: Displays commands that can be entered.\n")

def validateField(field, defaultVal):
    if(field.isnumeric()):
        return int(field)
    return defaultVal

def start_configuration():
    print("\n>>Define Thresholds for Params [Temperature | Humidity | Carbon Monoxide\n")
    tempMax = validateField(input("MAX THRESHHOLD TEMPERATURE (default: 35°C) : "), 35)
    tempMin = validateField(input("MIN THRESHHOLD TEMPERATURE (default: 20°C) : "), 20)
    humMax = validateField(input("MAX THRESHHOLD HUMIDITY (default: 80%rh) : "), 80)
    humMin = validateField(input("MIN THRESHHOLD HUMIDITY (default: 30%rh) : "), 30)
    co2Max = validateField(input("MAX THRESHHOLD CO2 (default: 2000ppm) : "), 2000)
    co2Min = validateField(input("MIN THRESHHOLD CO2 (default: 1000ppm) : "), 1000)
    
    print("\n>>Values for Thresholds: \n Max Temperature={}, \n Min Temperature={}, \n Max Humidity={}, \n Min Humidity={}, \n Max CO2={}, \n Min CO2={}"
    .format(str(tempMax), str(tempMin), str(humMax), str(humMin), str(co2Max), str(co2Min)))
    print("\n>>Do you wish to continue with these values? [y|n]")

    ans = input(">>")
    ans = ans.strip().lower()

    while 1:
        if(ans == "y" or ans == "yes"):
            return {
                "tempMax": tempMax,
                "tempMin": tempMin,
                "humMax": humMax,
                "humMin": humMin,
                "co2Max": co2Max,
                "co2Min": co2Min
            }
        elif(ans == "n" or ans == "no"):
            start_configuration()
        else:
            print("\n>>Please follow instructions. Press [y | n]")
            ans = input(">>")
            ans = ans.strip().lower()



if __name__ == "__main__":
    conf = {"tempMax": 35,"tempMin":20,"humMax":80,"humMin":30,"co2Max": 1800,"co2Min":1200}
    config_params = input("Welcome to Home Air Sensor simulator...\nDo you want to configure your parameters? [y|n]").strip().lower()
    if(config_params == "yes" or config_params == "y"):
        conf = start_configuration()
    
    print("\n>>Starting...")
    allCommands()

    print("\nSystem Initializing...\n")
    time.sleep(2)

    #Initialize the Thread for Client
    client = MqttClientData()
    thread = threading.Thread(
        target=client.mqtt_client,
        args=(
            conf["tempMax"], conf["tempMin"],
            conf["humMax"], conf["humMin"],
            conf["co2Max"], conf["co2Min"], "check"),
        kwargs={})
    thread.start()

    #Initialize for the Client 1
    client1 = MqttClientExtractionFilter()
    thread1 = threading.Thread(target=client1.mqtt_client, args=(), kwargs={})
    thread1.start()

    #Initialize for the Server
    server = CoAPServer(ip, port)
    thread2 = threading.Thread(target=server.listen(), args=(), kwargs={})
    thread2.start()
