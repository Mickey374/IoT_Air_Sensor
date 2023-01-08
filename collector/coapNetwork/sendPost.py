from coapthon.server.coap import CoAP
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.resources.resource import Resource

class Post:
    clients = {} #client list

    def getClients(ad):
        address = ''.join(ad[0])
        if address not in Post.clients:
            newClient = HelperClient(ad)
            Post.clients[address] = newClient
        client = Post.clients[address]
        return client
    
    def getStatusFilters(ad, status):
        res = Post.getClients(ad).post("obs", "mode="+status)

        if res.code == 67:
            return 1
        else:
            return 0
    
    def getStatusWindows(ad, status):
        res = Post.getClients(ad).post("window", "mode="+status)

        if res.code == 67:
            return 1
        else:
            return 0