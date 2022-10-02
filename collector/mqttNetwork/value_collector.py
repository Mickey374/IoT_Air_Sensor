from datetime import datetime
import json
import paho.mqtt.client as mqtt
from database.db import Database

class MqttClientProfile:
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
            self.carbonIn = carbon_monoxide
            self.humidityIn = humidity
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
        


    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mqtt.eclipseprojects.io", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()