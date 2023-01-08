from coapthon.resources.resource import Resource
from coapNetwork.sensor import ObserveSensor
from coapNetwork.addresses import Addresses

class ResExample(Resource):
    filters = 0
    windows = 0

    def __init__(self, name="ResExample"):
        super(ResExample, self).__init__(name)
        self.payload = "Advanced resource"
    
    def render_GET(self, request):
        if request.payload == "filters":
            Addresses.insertNewAddress(request.source, "filters")
            ResExample.valves = 1
            ob = ObserveSensor(request.source, "obs", 0)
        elif request.payload == "window":
            Addresses.insertNewAddress(request.source, "windows")
            ResExample.windows = 1
            ob = ObserveSensor(request.source, "window", 1)
        return self
    
    def checkPresenceValves():
        return ResExample.filters


    def checkPresenceFans():
        return ResExample.windows