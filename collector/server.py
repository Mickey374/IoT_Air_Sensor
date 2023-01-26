import getopt
import sys
import json
import threading
import time
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
from alert_resource import AlertResource
from poisonous_resource import PoisonResource

class AdvancedResource(Resource):
    def __init__(self, name="Advanced"):
        super(AdvancedResource, self).__init__(name)
        self.payload = "Advanced Resource"
    
    def render_GET_advanced(self, request, response):
        print("GET Server message: \n", request.payload)

        moteInfo = json.loads(request.payload)
        response.payload = self.payload

        response.max_age = 20
        response.code = defines.Codes.CONTENT.number

        moteInfo["Source"] = request.source
        motionResource = PoisonResource(moteInfo["Source"], moteInfo["Resource"])
        return self, response
    

class AdvancedResourceAlert(Resource):
    def __init__(self, name="AdvancedAlert"):
        super(AdvancedResourceAlert, self).__init__(name)
        self.payload = "Registration Successful"
    
    def render_GET_advanced(self, request, response):
        print("GET Server message: \n", request.payload)

        moteInfo = json.loads(request.payload)
        response.payload = self.payload

        response.max_age = 20
        response.code = defines.Codes.CONTENT.number

        moteInfo["Source"] = request.source
        alertResource = AlertResource(moteInfo["Source"], moteInfo["Resource"])
        return self, response