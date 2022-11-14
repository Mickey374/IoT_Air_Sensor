import imp
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from database.db import Database
from coapNetwork.addresses import Addresses
from coapNetwork.sendPost import Post
from globalStatus import globalStatus

class MqttClientData:
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        # print("Connected with result code "+str(rc))
        self.client.subscribe("temp_status_in")     #for temperature, humidity, carbon monoxide
        self.client.subscribe("temp_status_out")    #for temperature outside
        self.client.subscribe("actuator_out")       #initiate filter for external temperature sensor
        self.client.subscribe("actuator_in")        #initiate filter & fan for internal temperature sensor

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        if msg.topic == "temp_status_in":
            self.message = msg.payload
            data = json.loads(msg.payload)
            node_ID = data["node"]
            temperature = data["temperature"]
            carbon_monoxide = data["carbon_monoxide"]
            humidity = data["humidity"]
            self.tempIn = temperature
            self.co2In = carbon_monoxide
            self.humIn = humidity
            curr_date = datetime.now()
            cursor = self.connection.cursor()
            query = "INSERT INTO `node_data` (`node_id`, `timestamp`, `temperature`, `humidity`,  `carbon_monoxide`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (node_ID, curr_date, temperature, humidity, carbon_monoxide))
            self.connection.commit()
            self.checkActuatorFan(temperature, humidity, carbon_monoxide)
        
        elif msg.topic == "temp_status_out":
            self.message1 = msg.payload
            data = json.loads(msg.payload)
            node_ID = data["node"]
            tempOut = data["tempOut"]
            self.tempOut = tempOut
            self.checkActuatorFilter(tempOut)
    
    #Function to get most recent state of each actuator
    def executeCurrentState(self, address, table, col):
        cursor = self.connection.cursor()
        query = "SELECT * FROM actuator_"+table+" WHERE address=%s ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query, str(address))
        all_results = cursor.fetchall()
        if not all_results:
            return None
        else:
            for row in all_results:
                return row[col]

    #Function to communicate to the Sensors to Initiate  Action based on change
    def communicateToSensors(self, status, type):
        if type == "filter":
            if str(status) == "1":
                globalStatus.setFilterStatus(1)
                self.client.publish("actuator_data", "Open")
            elif str(status) == "0":
                globalStatus.setFilterStatus(0)
                self.client.publish("actuator_data", "Closed")
        elif type == "initFan":
            if str(status) == "1":
                globalStatus.setFanStatus(1)
                self.client.publish("actuator_data", "startFan")
            elif str(status) == "0":
                globalStatus.setFanStatus(0)
                self.client.publish("actuator_data", "stopFan")            

    # ======= Function declaration to open and close the Filters ==========
    def openFilters(self):
        for curr_add in Addresses.ad_Filters:
            open = self.executeCurrentState(curr_add, "filter", "status")
            manual =self.executeCurrentState(curr_add, "filter", "manual")

            if manual=='1' and open != '0':
                return
            if open is not None:
                if open =="0":
                    open = "1"
                    success = Post.getStatusFilters(curr_add, open)
                    if success == 1:
                        dt = datetime.now()
                        cursor = self.connection.cursor()
                        query = "INSERT INTO `actuator_filter` (`address`, `timestamp`, `status`) VALUES (%s, %s, %s)"
                        cursor.execute(query, (str(curr_add), dt, open))
                        if globalStatus.changeVal == 0:
                            print("\n ☢️☢️☢️ OPENING FILTERS ☢️☢️☢️\n")
                        self.connection.commit()
                        self.communicateToSensors("1", "filter")
            
            elif open is None:
                open = "1"
                success = Post.getStatusFilters(curr_add, open)
                if success == 1:
                    dt = datetime.now()
                    cursor = self.connection.cursor()
                    query = "INSERT INTO `actuator_filter` (`address`, `timestamp`, `status`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (str(curr_add), dt, open))
                    if globalStatus.changeVal == 0:
                        print("\n ☢️☢️☢️ OPENING FILTERS... ☢️☢️☢️\n")
                    self.connection.commit()
                    self.communicateToSensors("1", "filter")
    
    def closeFilters(self):
        for curr_add in Addresses.ad_Filters:
            open = self.executeCurrentState(curr_add, "filter", "Status")
            manual = self.executeCurrentState(curr_add, "filter", "manual")
            if manual == "1" and open != "0":
                return
            if open == "1":
                open = "0"
                success = Post.getStatusFilters(curr_add, open)
                if success == 1:
                        dt = datetime.now()
                        cursor = self.connection.cursor()
                        query = "INSERT INTO `actuator_filter` (`address`, `timestamp`, `status`) VALUES (%s, %s, %s)"
                        cursor.execute(query, (str(curr_add), dt, open))
                        if globalStatus.changeVal == 0:
                            print("\n 🚫🚫🚫 CLOSING FILTERS... 🚫🚫🚫\n")
                        self.connection.commit()
                        self.communicateToSensors("0", "filter")

    # ======== Function to start fan within the environment =============
    def startFan(self):
        for curr_add in Addresses.ad_Fans:
            status = self.executeCurrentState(curr_add, "fanning", "status")
            manual = self.executeCurrentState(curr_add, "fanning", "manual")
            if manual == "1" and status !="0":
                return
            if status is None:
                status = "1"
                success = Post.getStatusFan(curr_add, status)
                if success == 1:
                    dt = datetime.now()
                    cursor = self.connection.cursor()
                    query = "INSERT INTO `actuator_fan` (`address`,`timestamp`,`status`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (str(curr_add), dt, status))
                    if globalStatus.changeVal == 0:
                        print("\n ☢🌀😌 STARTING FAN... ☢🌀😌\n")
                    self.connection.commit()
                    self.communicateToSensors(status, "initFan")
            
            if status == "0":
                status = "1"
                success = Post.getStatusFan(curr_add, status)
                if success == 1:
                    dt = datetime.now()
                    cursor = self.connection.cursor()
                    query = "INSERT INTO `actuator_fan` (`address`,`timestamp`,`status`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (str(curr_add), dt, status))
                    if globalStatus.changeVal == 0:
                        print("\n ☢💨😌 STARTING FAN... ☢💨😌\n")
                    self.connection.commit()
                    self.communicateToSensors(status, "initFan")

    def stopFan(self):
        for curr_add in Addresses.ad_Fans:
            status = self.executeCurrentState(str(curr_add), "fanning", "status")
            manual = self.executeCurrentState(str(curr_add), "fanning", "manual")
            if manual == "1" and status != "0":
                return
            if status == "1":
                status = "0"
                success = Post.getStatusFan(curr_add, status)
                if success == 1:
                    dt = datetime.now()
                    cursor = self.connection.cursor()
                    query = "INSERT INTO `actuator_fan` (`address`,`timestamp`,`status`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (str(curr_add), dt, status))
                    if globalStatus.changeVal == 0:
                        print("\n ☢🔌⏹️ STOPPING FAN... ☢🔌⏹️\n")
                    self.connection.commit()
                    self.communicateToSensors(status, "initFan")

    # ======== Checking if Actuators should be started =========
    def shouldStartFan(self, temp, hum, max_temp, max_hum, min_hum):
        if temp > max_temp and hum < max_hum: return True
        if hum < min_hum: return True
        return False
    
    def checkActuatorFan(self, temp, hum, co2):
        if self.shouldStartFan(int(temp), int(hum), self.max_temp, self.max_hum, self.min_hum):
            self.startFan()
        else:
            self.stopFan()
    
    def checkActuatorFilters(self, tempOut):
        open_temp = 0
        open_co2 = 0

        #Control logic for controlling the temperature values
        if self.tempIn == None or self.tempOut == None or self.co2In == None:
            return
        if self.tempIn > self.max_temp and self.tempIn > tempOut:
            open_temp = 1
        elif self.tempIn > self.min_temp and self.tempIn > tempOut:
            open_temp = 0
        
        if self.co2In >  (self.max_co2 -100):
            open_co2 = 1
        elif self.co2In < (self.min_co2 +100):
            open_co2 = 0

        #Initiate the trigger for the actuator
        if open_temp ==1 and open_co2 ==1:
            self.openFilters()
        
        elif open_temp ==1 and open_co2 == 0:
            self.openFilters()
        
        elif open_temp == 0  and open_co2 == 1:
            self.openFilters()
        
        elif open_temp == 0 and open_co2 == 0:
            self.closeFilters()


    client = None
    def mqtt_client(self, max_temp, min_temp, max_hum, min_hum, max_co2, min_co2, type):
        self.db = Database()
        self.connection = self.db.connect()
        self.message = ""
        self.message1 = ""
        self.data = {}
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.max_co2 = max_co2
        self.min_co2 = min_co2
        self.max_hum = max_hum
        self.min_hum = min_hum
        self.tempIn = None
        self.tempOut = None
        self.co2In = None
        self.humIn = None
        self.type = type

        if type == "check":
            print("\n MQTT Client Starting ...Temperature | Humidity | CO2")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect

        if type == "check":
            self.client.on_message = self.on_message
        
        try:
            self.client.connect("127.0.0.1", 1883, 60)
        except Exception as e:
            print(str(e))
        
        if type == "check":
            self.client.loop_forever()