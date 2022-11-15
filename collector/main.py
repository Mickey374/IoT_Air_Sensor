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
    