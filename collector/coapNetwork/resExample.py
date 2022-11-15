from coapthon.resources.resource import Resource
from coapNetwork.sensor import ObserveSensor
from coapNetwork.addresses import Addresses

class ResExample(Resource):
    filters = 0
    fans = 0

    def __init__(self, name="ResExample"):
        super(ResExample, self).__init__(name)
        self.payload = "Advanced resource"
    
    def render_GET(self, request):
        if request.payload == "filters":
            Addresses.insertNewAddress(request.source, "valves")
            ResExample.valves = 1
            ob = ObserveSensor(request.source, "obs", 0)
        elif request.payload == "fan":
            Addresses.insertNewAddress(request.source, "fans")
            ResExample.windows = 1
            ob = ObserveSensor(request.sourcce, "fan", 1)
        return self
    
    def checkPresenceValves():
        return ResExample.filters


    def checkPresenceFans():
        return ResExample.fans