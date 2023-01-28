import threading
import logging
from coapthon.server.coap import CoAP
from mqtt_collector import MqttClient
from server import *

ip = "::"
port = 5683

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("registry", AdvancedResource())
    

def start_application():
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
        mqtt_thread.join()
        server.close()
        print("Exiting!")


if __name__ == '__main__':
    start_application()