import paho.mqtt.client as mqtt
import json
from time import sleep
from datetime import datetime
from collector.database import Database
# from pydoc import cli
from coapNetwork.addresses import Addresses
from coapNetwork.sendPost import Post
from globalStatus import globalStatus

class MqttClientExtractionFilter:
    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("status_gasExtractor")
        self.client.subscribe("actuator_gasExtractor")
    
    def update_gas_monitoring_status(self, ad, status):
        dt = datetime.now()
        cursor = self.connection.cursor()
        query = "INSERT INTO `actuator_fan` (`address`, `timestamp`, `status`) VALUES (%s, %s, %s)"
        cursor.execute(query, (str(ad), dt, status))
        print("\nSTATUS = "+ status)
        self.connection.commit()
    
    def update_gas_monitoring_mode(self, node_id, mode):
        dt = datetime.now()
        cursor = self.connection.cursor()
        query = "INSERT INTO `gas_extractor` (`node_id`, `timestamp`, `mode`) VALUES (%s, %s, %s)"
        cursor.execute(query, (str(node_id), dt, mode))
        self.connection.commit()

    #This will be the callback for when a publish message is received from server
    def on_message(self, client, userdata, msg):
        #check the type of message received
        if(msg.topic == "status_gasExtractor"):
            self.message = msg.payload
            data = json.loads(msg.payload)
            node_id = data["node"]
            level = data["level"]
            self.levIn = level
            self.update_gas_monitoring_mode(node_id, level)
            self.checkActuatorMode(level)
        else:
            return
    
    ##Method to on/off the charge valve for the extractor
    def offCharge(self):
        for ad in Addresses.ad_Filters:
            status = self.executeLastState(ad, "filtering", "status")
            manual = self.executeLastState(ad, "filtering", "manual")
            if manual =="1" and status!= "0":
                return
            if status=="2":
                status = "0"
                sleep(1)
                success = Post.getStatusFilters(ad, status)
                if success == 1:
                    self.update_gas_monitoring_status(str(ad), "0")
                    if globalStatus.changeVal == 0: print("\n📴📴CHARGE DISPENSER CLOSED📴📴\n")
                    self.connection.commit()
                    self.communicateToSensors("0")
            else:
                return
    
    def onCharge(self):
        for ad in Addresses.ad_Filters:
            status = self.executeLastState(ad, "filtering", "status")
            manual = self.executeLastState(ad, "filtering", "manual")
            if manual =="1" and status!= "0":
                return
            if status=="0":
                status = "2"
                sleep(1)
                success = Post.getStatusFilters(ad, status)
                if success == 1:
                    self.update_gas_monitoring_status(str(ad), status)
                    if globalStatus.changeVal == 0: print("\n🔛🔛CHARGE DISPENSER CLOSED🔛🔛\n")
                    self.communicateToSensors("2")
            
            if status is None:
                status = "2"
                success = Post.getStatusFilters(ad, status)
                if success == 1:
                    self.update_gas_monitoring_status(str(ad), status)
                    if globalStatus.changeVal == 0: print("\n🔛🔛CHARGE DISPENSER CLOSED🔛🔛\n")
                    self.communicateToSensors("2")
    

    #Function to retrieve last state and address of actuator
    def executeLastState(self, address, table, column):
        cursor = self.connection.cursor()
        query = "SELECT * FROM actuator_"+table+" WHERE address=%s ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query, str(address))
        result_vals = cursor.fetchall()
        if not result_vals:
            return None
        else:
            for resp in result_vals:
                return resp[column]
    
    def checkExtractorMode(self, level):
        if level < 20:
            self.onCharge()
        elif level > 80:
            self.offCharge()
        else:
            return
    
    #Function to notify status change for actuators
    def communicateToSensors(self, status):
        if status == "2":
            self.client.publish("actuator_gasExtractor", "charge")
        elif status == "0":
            self.client.publish("actuator_gasExtractor", "stop")
    
    def mqtt_client(self):
        self.db = Database()
        self.connection = self.db.connect()
        self.message = ""
        self.level = 80
        self.levIn = None
        print("\n⛽⛽MQTT Client Gas Extraction starting...⛽⛽\n")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect("127.0.0.1", 1883, 60)
        except Exception as e:
            print(str(e))

        self.client.loop_forever()