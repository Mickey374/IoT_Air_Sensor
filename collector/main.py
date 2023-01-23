import threading
import os
import logging
import time
from coapthon.server.coap import CoAP
from mqtt_collector import MQTTClient
from server import *

ip = "::"
port = 5683

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("registry", AdvancedResource())
    
def allCommands():
    print(">> ALL COMMANDS TO START \n")
    print(
    "help \n"\
    "logs\n"\
    "simulate\n"\
    "exit\n\n")

def checkUserCommand(command, client):
    if command == "help":
        showInfo()
    
    elif command == "logs":
        try:
            msg = str(client.message)
            print("\n>>Press Ctrl+C to terminate session \n")
            while True:
                time.sleep(1)
                if(str(client.message) != msg):
                    print("\n>>"+str(client.message))
                    msg = str(client.message)
        except KeyboardInterrupt:
            return   
        
    elif command == "exit":
        print("\n>>Shutting Down")
        os._exit(0)

    else:
        print("/n>>Retry Commands Again...")
        allCommands()


def showInfo():
        print("\n"\
            ">>logs: Displays messages that the sensors delivers to the app \n"\
            ">>help: Displays commands that can be entered.\n")


def test():
    logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
    logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
    logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)

    client = MQTTClient()
    thread = threading.Thread(target=client.mqtt_client, args=(), kwargs={})
    thread.start()

    server = CoAPServer(ip, port)

    time.sleep(5)
    try:
        server.listen(100)
    except KeyboardInterrupt:
        print("\n🔐🔐SYSTEM CLOSING🔐🔐\n")
        thread.join()
        server.close()
        os._exit(0)

if __name__ == "__main__":
    print("\n>>Starting...")
    allCommands()
    
    time.sleep(2)
    test()